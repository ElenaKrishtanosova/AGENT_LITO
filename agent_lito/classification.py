"""
LLM классификация пользовательских запросов
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .data_types import ClassificationResult, QueryType


class QueryClassifier:
    """Классификатор запросов на основе LLM"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    async def classify(self, user_input: str) -> ClassificationResult:
        """LLM-классификация пользовательского запроса"""
        
        system_prompt = """You are a helpful AI assistant that parses queries, following instructions and classifies input query into four categories:

- DATABASE_SEARCH: if the user wants to get resources or is looking for help or support with issues such as Clothing/Supplies, Financial, Food, Childcare, Activities, Housing, Mental Health, Physical Health, Education, Employment, or Legal Issues. These are free resources specifically for families with foster children.

- WEB_SEARCH: if the user wants to search for resources on the internet using search engines, contains words like "find", "search online", "google", "look up online".

- URL_SEARCH: if the user provides a specific URL/link and wants to search or analyze content from that particular website, contains "http", "www", "website", "link", ".com", ".org".

- UNCLEAR_QUERY: if the query is unclear, ambiguous, or doesn't clearly fit into the above categories related to resource searching.

LOCATION EXTRACTION:
This bot is designed for families with foster children looking for FREE resources in their specific location. Location is CRITICAL for most queries.

- ALWAYS extract location information if present in the query
- If location is mentioned, extract it in JSON format: {"city": "", "county": "", "state": ""}
- If NO location is provided but the query is about finding resources, set location_needed to true
- For DATABASE_SEARCH and WEB_SEARCH, location is almost always needed unless it's a very general informational query

KEYWORDS EXTRACTION:
Extract relevant keywords related to:
- Resource categories (food, housing, clothing, childcare, mental health, etc.)
- Specific needs or problems
- Age groups (children, teens, infants, etc.)
- Any other relevant search terms

Analyze the query carefully and return the result in the specified JSON format with high confidence scores for clear queries."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Classify this query: {user_input}")
        ]

        try:
            # Используем structured output для получения ClassificationResult
            result = await self.llm.with_structured_output(ClassificationResult).ainvoke(messages)
            
            print(f"🤖 LLM Classification:")
            print(f"   Type: {result.query_type}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Keywords: {result.extracted_keywords}")
            print(f"   Location needed: {result.location_needed}")
            if result.location_info:
                print(f"   Location: {result.location_info}")
            
            return result
            
        except Exception as e:
            print(f"❌ LLM classification error: {e}")
            # Возвращаем UNCLEAR_QUERY при ошибке
            return ClassificationResult(
                query_type=QueryType.UNCLEAR_QUERY,
                confidence=0.0,
                extracted_keywords=[],
                location_needed=False
            ) 