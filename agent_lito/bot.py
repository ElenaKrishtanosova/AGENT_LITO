"""
Main LangGraph chatbot class for resource discovery
"""

import os
import asyncio
from typing import Literal

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langchain_openai import ChatOpenAI

# Internal modules
from .data_types import ChatState, QueryType, ResourceItem, LocationInfo
from .classification import QueryClassifier
from .search import DatabaseSearcher, WebSearcher, URLSearcher


class ResourceChatBot:
    """Primary chatbot class for finding resources for foster families"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1
        )
        
        # Initialize components
        self.classifier = QueryClassifier(self.llm)
        self.db_searcher = DatabaseSearcher(os.getenv("CONN_STRING"))
        self.web_searcher = WebSearcher(os.getenv("TAVILY_API_KEY"))
        self.url_searcher = URLSearcher()
        
        # Graph setup
        self.workflow = self._build_graph()
        self.app = self.workflow.compile(checkpointer=MemorySaver())
    
    def _build_graph(self) -> StateGraph:
        """Build state graph with dynamic navigation"""
        workflow = StateGraph(ChatState)
        
        # Add nodes
        workflow.add_node("classify_query", self._classify_query_node)
        workflow.add_node("check_location", self._check_location_node)
        workflow.add_node("location_response", self._location_response_node)
        workflow.add_node("search_database", self._search_database_node)
        workflow.add_node("search_web", self._search_web_node)
        workflow.add_node("search_url", self._search_url_node)
        workflow.add_node("handle_unclear", self._handle_unclear_node)
        workflow.add_node("generate_response", self._generate_response_node)
        
        # Start node
        workflow.add_edge(START, "classify_query")
        
        # Conditional edges from classify_query
        workflow.add_conditional_edges(
            "classify_query",
            lambda state: getattr(state, 'next_node', 'generate_response'),
            {
                "check_location": "check_location",
                "search_database": "search_database", 
                "search_web": "search_web",
                "search_url": "search_url",
                "handle_unclear": "handle_unclear",
                "generate_response": "generate_response"
            }
        )
        
        # Conditional edges from check_location
        workflow.add_conditional_edges(
            "check_location",
            lambda state: getattr(state, 'next_node', 'generate_response'),
            {
                "classify_query": "classify_query",
                "search_database": "search_database",
                "search_web": "search_web", 
                "search_url": "search_url",
                "location_response": "location_response",
                "generate_response": "generate_response"
            }
        )
        
        # Direct edges to generate_response
        workflow.add_edge("search_database", "generate_response")
        workflow.add_edge("search_web", "generate_response")
        workflow.add_edge("search_url", "generate_response")
        workflow.add_edge("handle_unclear", "generate_response")
        workflow.add_edge("location_response", "generate_response")
        
        # Final edge
        workflow.add_edge("generate_response", END)
        
        return workflow
    
    # === GRAPH NODES ===
    
    async def _classify_query_node(self, state: ChatState) -> Command:
        """Node for classifying user query"""
        print(f"🔍 Classifying query: {state.user_input}")
        
        # LLM classification
        classification = await self.classifier.classify(state.user_input)
        
        # Determine location from classification or use existing one
        # But only if it's not a new query (not from check_location)
        user_location = None
        if hasattr(state, 'from_location_check') and state.from_location_check:
            # If we came from check_location, use the saved location
            user_location = state.user_location
        else:
            # For a new query, use the location from classification
            user_location = classification.location_info
        
        # Check if location is needed and if it exists
        needs_location_check = classification.location_needed and (
            user_location is None or 
            (hasattr(user_location, 'city') and not user_location.city) or
            (hasattr(user_location, 'state') and not user_location.state)
        )
        
        print(f"   Location needed: {classification.location_needed}")
        print(f"   Current location: {user_location}")
        print(f"   Needs location check: {needs_location_check}")
        
        # Dynamic navigation based on query type
        if classification.query_type == QueryType.DATABASE_SEARCH:
            if needs_location_check:
                print("   → Going to check_location (needs location)")
                next_node = "check_location"
            else:
                print("   → Going to search_database")
                next_node = "search_database"
        elif classification.query_type == QueryType.WEB_SEARCH:
            if needs_location_check:
                print("   → Going to check_location (needs location)")
                next_node = "check_location"
            else:
                print("   → Going to search_web")
                next_node = "search_web"
        elif classification.query_type == QueryType.URL_SEARCH:
            if needs_location_check:
                print("   → Going to check_location (needs location)")
                next_node = "check_location"
            else:
                print("   → Going to search_url")
                next_node = "search_url"
        else:  # UNCLEAR_QUERY
            print("   → Going to handle_unclear")
            next_node = "handle_unclear"
        
        return Command(
            update={
                "classification": classification,
                "query_type": classification.query_type,
                "search_keywords": classification.extracted_keywords,
                "needs_location": classification.location_needed,
                "user_location": user_location,
                "from_location_check": False,  # Reset flag
                "next_node": next_node
            }
        )
    
    async def _check_location_node(self, state: ChatState) -> Command:
        """Node for checking and requesting location"""
        print("📍 Checking location requirements")
        
        # Check if location exists and if it's needed
        has_location = (
            state.user_location is not None and
            hasattr(state.user_location, 'city') and 
            state.user_location.city and
            hasattr(state.user_location, 'state') and 
            state.user_location.state
        )
        
        if not has_location and state.needs_location:
            # Real interrupt for requesting location from user
            print("   🔄 INTERRUPT: Requesting location from user")
            
            # Return message for location request
            return Command(
                update={
                    "interrupt_message": "For resource discovery, I need your location. Please specify city and state (e.g., Austin, Texas):",
                    "waiting_for_location": True,
                    "original_query": state.user_input,
                    "search_keywords": state.search_keywords,
                    "query_type": state.query_type,
                    "next_node": "generate_response"
                }
            )
        
        # Location already exists or not needed - proceed to relevant search
        if state.query_type == QueryType.DATABASE_SEARCH:
            next_node = "search_database"
        elif state.query_type == QueryType.WEB_SEARCH:
            next_node = "search_web"
        else:  # URL_SEARCH
            next_node = "search_url"
            
        return Command(
            update={
                "next_node": next_node
            }
        )
    
    async def _location_response_node(self, state: ChatState) -> Command:
        """Node for processing location response from user"""
        print("📍 Processing location response from user")
        
        # Parse location from user response
        location_text = state.user_input.strip()
        
        # Simple location parsing (can be improved with LLM)
        if "," in location_text:
            parts = [part.strip() for part in location_text.split(",")]
            if len(parts) >= 2:
                city = parts[0]
                state = parts[1]
                county = parts[2] if len(parts) > 2 else None
            else:
                city = parts[0]
                state = parts[1]
                county = None
        else:
            # If no comma, consider the entire text as the city
            city = location_text
            state = None
            county = None
        
        location_info = LocationInfo(
            city=city,
            county=county,
            state=state
        )
        
        print(f"   Parsed location: {location_info}")
        
        # Return to search with obtained location
        if state.query_type == QueryType.DATABASE_SEARCH:
            next_node = "search_database"
        elif state.query_type == QueryType.WEB_SEARCH:
            next_node = "search_web"
        else:  # URL_SEARCH
            next_node = "search_url"
        
        return Command(
            update={
                "user_location": location_info,
                "waiting_for_location": False,
                "interrupt_message": None,
                "next_node": next_node
            }
        )
    
    async def _search_database_node(self, state: ChatState) -> Command:
        """Node for searching in Azure SQL database"""
        print(f"   Searching for keywords: {state.search_keywords}")
        resources = await self.db_searcher.search(state.search_keywords)
        print(f"   Found {len(resources)} resources from database")
        
        if resources:
            print(f"   First resource title: {resources[0].title}")
        
        # Update state with found resources
        return Command(
            update={
                "found_resources": resources,
                "query_type": state.query_type,
                "user_location": state.user_location,
                "next_node": "generate_response"
            }
        )
    
    async def _search_web_node(self, state: ChatState) -> Command:
        """Node for searching the internet"""
        location_str = self._format_location(state.user_location) if state.user_location else None
        resources = await self.web_searcher.search(state.search_keywords, location_str)
        
        return Command(
            update={
                "found_resources": resources,
                "next_node": "generate_response"
            }
        )
    
    async def _search_url_node(self, state: ChatState) -> Command:
        """Node for searching a specific URL"""
        resources = await self.url_searcher.search(state.search_url, state.search_keywords)
        
        return Command(
            update={
                "found_resources": resources,
                "next_node": "generate_response"
            }
        )
    
    async def _handle_unclear_node(self, state: ChatState) -> Command:
        """Node for handling unclear queries"""
        print("❓ Handling unclear query")
        
        new_attempts = state.clarification_attempts + 1
        
        if new_attempts >= 2:
            # Politely end the conversation
            return Command(
                update={
                    "is_conversation_complete": True,
                    "clarification_attempts": new_attempts,
                    "final_response": "I'm sorry, I couldn't understand what specific resources you need for your foster family. Please try rephrasing your request more specifically, such as 'I need food assistance in Austin, Texas' or 'Looking for childcare resources in my area'.",
                    "next_node": "generate_response"
                }
            )
        
        # TODO: Here should be an interrupt for requesting clarification
        # For now, we mock
        clarification = "I need food assistance for my foster children in Austin, Texas"
        
        return Command(
            update={
                "user_input": clarification,
                "clarification_attempts": new_attempts,
                "next_node": "classify_query"
            }
        )
    
    async def _generate_response_node(self, state: ChatState) -> Command:
        """Node for generating the final response"""
        print("📝 Generating final response")
        print(f"   Found resources: {len(state.found_resources) if state.found_resources else 0}")
        print(f"   Query type: {state.query_type}")
        print(f"   Is conversation complete: {state.is_conversation_complete}")
        
        if state.found_resources:
            print(f"   First resource: {state.found_resources[0].title}")
        
        if state.is_conversation_complete:
            response = state.final_response
        else:
            # Generate response based on found resources
            response = self._format_response(state.found_resources, state.query_type, state.user_location)
        
        print(f"   Generated response length: {len(response)}")
        
        return Command(
            update={
                "final_response": response,
                "is_conversation_complete": True,
                "next_node": END
            }
        )
    
    # === HELPER METHODS ===
    
    def _format_location(self, location: LocationInfo) -> str:
        """Formats LocationInfo to string"""
        parts = []
        if location.city:
            parts.append(location.city)
        if location.county:
            parts.append(location.county)
        if location.state:
            parts.append(location.state)
        return ", ".join(parts)
    
    def _format_response(self, resources: list[ResourceItem], query_type: QueryType, location: LocationInfo = None) -> str:
        """Formats response based on found resources"""
        if not resources:
            location_str = f" in {self._format_location(location)}" if location else ""
            return f"I couldn't find any free resources for foster families{location_str}. Please try a different search or contact your local foster care agency for assistance."
        
        location_str = f" in {self._format_location(location)}" if location else ""
        response = f"Found {len(resources)} free resources for foster families{location_str}:\n\n"
        
        for i, resource in enumerate(resources, 1):
            response += f"{i}. **{resource.title}**\n"
            response += f"   {resource.description}\n"
            response += f"   Category: {resource.category}\n"
            if resource.location:
                response += f"   Location: {resource.location}\n"
            if resource.url:
                response += f"   Website: {resource.url}\n"
            if resource.contact_info:
                response += f"   Contact: {resource.contact_info}\n"
            response += f"   Relevance: {resource.relevance_score:.1%}\n\n"
        
        return response
    
    # === PUBLIC METHODS ===
    
    async def process_user_query(self, user_input: str) -> str:
        """
        Main method for processing user query
        
        Args:
            user_input: User query
            
        Returns:
            Final system response or interrupt message
        """
        config = {"configurable": {"thread_id": "user_session"}}
        
        # Run graph
        result = await self.app.ainvoke(
            {"user_input": user_input},
            config=config
        )
        
        # Check for interrupt
        if result.get("interrupt_message"):
            return result["interrupt_message"]
        
        return result.get("final_response", "An error occurred while processing your request.")
    
    async def process_user_query_with_resources(self, user_input: str) -> dict:
        """
        Processes user query and returns response with resources
        
        Args:
            user_input: User query
            
        Returns:
            Dictionary with response and found resources
        """
        config = {"configurable": {"thread_id": "user_session"}}
        
        # Run graph
        result = await self.app.ainvoke(
            {"user_input": user_input},
            config=config
        )
        
        # Check for interrupt
        if result.get("interrupt_message"):
            return {
                "response": result["interrupt_message"],
                "interrupt": True,
                "resources": []
            }
        
        # Convert resources to API format
        resources = []
        if result.get("found_resources"):
            for resource in result["found_resources"]:
                resources.append({
                    "title": resource.title,
                    "description": resource.description,
                    "category": resource.category,
                    "source": "Database Search",
                    "relevance_score": getattr(resource, 'relevance_score', 0.0),
                    "location": resource.location,
                    "url": resource.url,
                    "contact_info": resource.contact_info
                })
        
        return {
            "response": result.get("final_response", "An error occurred while processing your request."),
            "interrupt": False,
            "resources": resources
        }
    
    def get_mermaid_graph(self) -> str:
        """Returns Mermaid representation of the graph"""
        return self.app.get_graph().draw_mermaid() 