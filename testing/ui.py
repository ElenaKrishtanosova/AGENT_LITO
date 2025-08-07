"""
Streamlit UI для тестирования модулей чат-бота
"""

import streamlit as st
import requests
import json
from typing import List, Dict, Any

# Конфигурация
API_BASE_URL = "http://localhost:8000"

def test_classification(query: str) -> Dict[str, Any]:
    """Тестирование классификатора"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/classify",
            json={"query": query}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def test_database_search(keywords: List[str]) -> List[Dict[str, Any]]:
    """Тестирование поиска в БД"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/database-search",
            json={"keywords": keywords}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

def test_web_search(keywords: List[str], location: str = None) -> List[Dict[str, Any]]:
    """Тестирование веб-поиска"""
    try:
        payload = {"keywords": keywords}
        if location:
            payload["location"] = location
            
        response = requests.post(
            f"{API_BASE_URL}/web-search",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

def test_url_search(url: str, keywords: List[str]) -> List[Dict[str, Any]]:
    """Тестирование поиска по URL"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/url-search",
            json={"url": url, "keywords": keywords}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

def test_full_bot(user_input: str) -> Dict[str, Any]:
    """Тестирование полного бота"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/full-bot",
            json={"user_input": user_input}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def test_location_response(original_query: str, location: str) -> Dict[str, Any]:
    """Тестирование ответа с локацией"""
    try:
        print(f"🔍 UI: Sending request to API with location: {location}")
        response = requests.post(
            f"{API_BASE_URL}/location-response",
            json={"original_query": original_query, "location": location}
        )
        response.raise_for_status()
        result = response.json()
        print(f"🔍 UI: Received response from API: {len(str(result))} chars")
        print(f"🔍 UI: Response starts with: {result.get('response', '')[:100]}")
        return result
    except Exception as e:
        print(f"❌ UI: Error in test_location_response: {e}")
        return {"error": str(e)}

def display_classification_result(result: Dict[str, Any]):
    """Отображение результата классификации"""
    if "error" in result:
        st.error(f"Error: {result['error']}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Query Type", result["query_type"])
        st.metric("Confidence", f"{result['confidence']:.2%}")
    
    with col2:
        st.metric("Location Needed", "Yes" if result["location_needed"] else "No")
        if result["location_info"]:
            location = result["location_info"]
            st.metric("Location", f"{location.get('city', '')}, {location.get('state', '')}")
    
    st.subheader("Extracted Keywords")
    keywords = result.get("keywords", [])
    if keywords:
        for keyword in keywords:
            st.write(f"• {keyword}")
    else:
        st.write("No keywords extracted")

def display_resources(resources: List[Dict[str, Any]], title: str):
    """Отображение найденных ресурсов"""
    st.subheader(title)
    
    if not resources:
        st.warning("No resources found")
        return
    
    for i, resource in enumerate(resources, 1):
        if "error" in resource:
            st.error(f"Error: {resource['error']}")
            continue
            
        with st.expander(f"{i}. {resource['title']}"):
            st.write(f"**Description:** {resource['description']}")
            st.write(f"**Category:** {resource['category']}")
            st.write(f"**Source:** {resource['source']}")
            st.write(f"**Relevance:** {resource['relevance_score']:.1%}")
            if resource.get("location"):
                st.write(f"**Location:** {resource['location']}")
            if resource.get("url"):
                st.write(f"**Website:** [{resource['url']}]({resource['url']})")
            if resource.get("contact_info"):
                st.write(f"**Contact:** {resource['contact_info']}")

def main():
    st.set_page_config(
        page_title="Foster Family Resource Bot Testing",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Foster Family Resource Bot Testing")
    st.markdown("---")
    
    # Боковая панель для навигации
    st.sidebar.title("Testing Modules")
    test_mode = st.sidebar.selectbox(
        "Choose Module to Test",
        ["Classification", "Database Search", "Web Search", "URL Search", "Full Bot"]
    )
    
    # Проверка подключения к API
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            st.sidebar.success("✅ API Connected")
        else:
            st.sidebar.error("❌ API Connection Failed")
            st.error("Please start the API server first: `uv run python testing/api.py`")
            return
    except:
        st.sidebar.error("❌ API Connection Failed")
        st.error("Please start the API server first: `uv run python testing/api.py`")
        return
    
    # Основной контент
    if test_mode == "Classification":
        st.header("🔍 LLM Classification Testing")
        
        query = st.text_area(
            "Enter your query:",
            value="I need food assistance for my foster children in Austin, Texas",
            height=100
        )
        
        if st.button("🚀 Test Classification"):
            with st.spinner("Classifying query..."):
                result = test_classification(query)
                display_classification_result(result)
    
    elif test_mode == "Database Search":
        st.header("🗄️ Azure SQL Database Search Testing")
        st.info("🔍 **Azure SQL with Vector Support** - Testing vector similarity search in Azure SQL database")
        
        col1, col2 = st.columns(2)
        
        with col1:
            keywords_input = st.text_area(
                "Enter keywords (one per line):",
                value="food\nassistance\nfoster\nchildren",
                height=150
            )
        
        with col2:
            st.markdown("**Example keywords for Azure SQL:**")
            st.markdown("• food, assistance, foster, children")
            st.markdown("• clothing, supplies, free")
            st.markdown("• childcare, daycare")
            st.markdown("• mental, health, therapy")
            st.markdown("• medical, care, children")
        
        keywords = [kw.strip() for kw in keywords_input.split('\n') if kw.strip()]
        
        if st.button("🔍 Search Azure SQL Database"):
            with st.spinner("Searching Azure SQL database with vector similarity..."):
                resources = test_database_search(keywords)
                display_resources(resources, "Azure SQL Database Search Results")
    
    elif test_mode == "Web Search":
        st.header("🌐 Web Search Testing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            keywords_input = st.text_area(
                "Enter keywords (one per line):",
                value="mental health\nfoster families",
                height=150
            )
            location = st.text_input("Location (optional):", value="Austin, Texas")
        
        with col2:
            st.markdown("**Example queries:**")
            st.markdown("• mental health, foster families")
            st.markdown("• food assistance, Austin")
            st.markdown("• childcare resources")
            st.markdown("• housing support")
        
        keywords = [kw.strip() for kw in keywords_input.split('\n') if kw.strip()]
        
        if st.button("🌐 Search Web"):
            with st.spinner("Searching web..."):
                resources = test_web_search(keywords, location if location else None)
                display_resources(resources, "Web Search Results")
    
    elif test_mode == "URL Search":
        st.header("🔗 URL Search Testing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            url = st.text_input("URL:", value="https://fostercare.gov")
            keywords_input = st.text_area(
                "Enter keywords (one per line):",
                value="housing\nresources",
                height=150
            )
        
        with col2:
            st.markdown("**Example URLs:**")
            st.markdown("• https://fostercare.gov")
            st.markdown("• https://adoptuskids.org")
            st.markdown("• https://childwelfare.gov")
        
        keywords = [kw.strip() for kw in keywords_input.split('\n') if kw.strip()]
        
        if st.button("🔗 Search URL"):
            with st.spinner("Searching URL..."):
                resources = test_url_search(url, keywords)
                display_resources(resources, "URL Search Results")
    
    elif test_mode == "Full Bot":
        st.header("🤖 Full Bot Testing (Azure SQL Integrated)")
        st.info("🚀 **Complete LangGraph Workflow** - Testing the full bot with Azure SQL database integration")
        
        # Инициализация session state
        if "location_interrupt" not in st.session_state:
            st.session_state.location_interrupt = False
        if "original_query" not in st.session_state:
            st.session_state.original_query = ""
        if "interrupt_message" not in st.session_state:
            st.session_state.interrupt_message = ""
        if "bot_response" not in st.session_state:
            st.session_state.bot_response = None
        if "location_result" not in st.session_state:
            st.session_state.location_result = None
        
        # Если есть interrupt, показываем поле для ввода локации
        if st.session_state.location_interrupt:
            st.warning("🔄 **Location Required**")
            st.write(st.session_state.interrupt_message)
            
            # Используем форму для лучшего UX
            with st.form(key="location_form"):
                location_input = st.text_input(
                    "Please enter your location (city, state):",
                    placeholder="e.g., Austin, Texas",
                    help="Enter your city and state to help find local resources"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    submit_location = st.form_submit_button("📍 Submit Location", type="primary")
                with col2:
                    cancel_location = st.form_submit_button("❌ Cancel", type="secondary")
                
                if submit_location and location_input.strip():
                    with st.spinner("Processing with location..."):
                        location_result = test_location_response(
                            st.session_state.original_query, 
                            location_input
                        )
                        
                        # ВЫВОДИМ ВСЕ, ЧТО ПОЛУЧАЕМ ОТ API
                        st.write("🔍 DEBUG: Полный ответ от API:")
                        st.json(location_result)
                        
                        if "error" in location_result:
                            st.error(f"Error: {location_result['error']}")
                        else:
                            st.session_state.location_result = location_result
                            st.session_state.location_interrupt = False
                            st.session_state.original_query = ""
                            st.session_state.interrupt_message = ""
                            st.rerun()
                
                elif cancel_location:
                    st.session_state.location_interrupt = False
                    st.session_state.original_query = ""
                    st.session_state.interrupt_message = ""
                    st.rerun()
        
        # Если есть результат с локацией, показываем его
        elif st.session_state.location_result:
            st.success("✅ Location processed successfully!")
            
            location_result = st.session_state.location_result
            
            # Показываем результат
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Location Details")
                st.write(f"**Location:** {location_result.get('location', 'N/A')}")
                st.write(f"**Query Type:** {location_result.get('query_type', 'N/A')}")
                st.write(f"**Keywords:** {', '.join(location_result.get('keywords', []))}")
            
            with col2:
                st.subheader("🤖 Bot Information")
                st.write(f"**Bot Type:** {location_result.get('bot_type', 'Azure SQL Integrated Bot')}")
                st.write(f"**Database:** Azure SQL with Vector Support")
                st.write(f"**LLM:** OpenAI GPT-4o-mini")
            
            # Показываем ответ
            st.subheader("📝 Bot Response")
            st.write(location_result.get("response", "No response"))
            
            # Если есть ресурсы, показываем их
            if location_result.get("resources"):
                st.subheader("📋 Found Resources")
                display_resources(location_result["resources"], "Database Search Results")
            
            # Кнопка для нового запроса
            if st.button("🔄 New Query"):
                st.session_state.location_result = None
                st.rerun()
        
        # Основной интерфейс для ввода запроса
        else:
            # Поле для ввода запроса
            user_input = st.text_area(
                "Enter your request:",
                value="Where can I find mental health resources for foster families?",
                height=100,
                help="Ask about resources, services, or information for foster families"
            )
            
            # Кнопка для отправки запроса
            if st.button("🤖 Test Full Bot", type="primary"):
                with st.spinner("Processing with Azure SQL integrated bot..."):
                    result = test_full_bot(user_input)
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    elif result.get("interrupt"):
                        # Обрабатываем interrupt для запроса локации
                        st.session_state.location_interrupt = True
                        st.session_state.original_query = user_input
                        st.session_state.interrupt_message = result.get("message", "Location needed")
                        st.rerun()
                    else:
                        # Показываем обычный ответ
                        st.session_state.bot_response = result
                        
                        # Показываем результат
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("📊 Query Details")
                            st.write(f"**Query Type:** {result.get('query_type', 'N/A')}")
                            st.write(f"**Keywords:** {', '.join(result.get('keywords', []))}")
                            if result.get('location'):
                                st.write(f"**Location:** {result.get('location')}")
                        
                        with col2:
                            st.subheader("🤖 Bot Information")
                            st.write(f"**Bot Type:** {result.get('bot_type', 'Azure SQL Integrated Bot')}")
                            st.write(f"**Database:** Azure SQL with Vector Support")
                            st.write(f"**LLM:** OpenAI GPT-4o-mini")
                        
                        # Показываем ответ
                        st.subheader("📝 Bot Response")
                        st.write(result.get("response", "No response"))
                        
                        # Если есть ресурсы, показываем их
                        if result.get("resources"):
                            st.subheader("📋 Found Resources")
                            display_resources(result["resources"], "Database Search Results")
                        
                        # Кнопка для нового запроса
                        if st.button("🔄 New Query"):
                            st.session_state.bot_response = None
                            st.rerun()
    


    # Секция тестирования отдельных модулей

    # Информация о системе
    st.sidebar.markdown("---")
    st.sidebar.markdown("**System Info:**")
    st.sidebar.markdown("• API: FastAPI + Uvicorn")
    st.sidebar.markdown("• UI: Streamlit")
    st.sidebar.markdown("• LLM: OpenAI GPT-4o-mini")
    st.sidebar.markdown("• Database: Azure SQL with Vector Support")
    st.sidebar.markdown("• Purpose: Foster Family Resources")
    st.sidebar.markdown("• Bot Type: Azure SQL Integrated Bot")

if __name__ == "__main__":
    main() 