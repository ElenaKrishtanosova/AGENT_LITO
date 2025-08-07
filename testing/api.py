"""
FastAPI сервер для тестирования модулей чат-бота
"""

import asyncio
from typing import List, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Импортируем модули из основного пакета
from agent_lito import ResourceChatBot
from agent_lito.data_types import ClassificationResult, ResourceItem, LocationInfo
from agent_lito.classification import QueryClassifier
from agent_lito.search import DatabaseSearcher, WebSearcher, URLSearcher


# Pydantic модели для API
class ClassificationRequest(BaseModel):
    query: str

class ClassificationResponse(BaseModel):
    query_type: str
    confidence: float
    keywords: List[str]
    location_needed: bool
    location_info: Optional[dict] = None

class DatabaseSearchRequest(BaseModel):
    keywords: List[str]

class WebSearchRequest(BaseModel):
    keywords: List[str]
    location: Optional[str] = None

class URLSearchRequest(BaseModel):
    url: Optional[str] = None
    keywords: List[str]

class ResourceResponse(BaseModel):
    title: str
    description: str
    category: str
    source: str
    relevance_score: float
    location: Optional[str] = None
    url: Optional[str] = None
    contact_info: Optional[str] = None

class FullBotRequest(BaseModel):
    user_input: str

class FullBotResponse(BaseModel):
    response: str
    classification: Optional[ClassificationResponse] = None
    resources: List[ResourceResponse] = []

class LocationResponseRequest(BaseModel):
    original_query: str
    location: str

class LocationResponseResponse(BaseModel):
    success: bool
    response: str
    query_type: str
    location: str
    keywords: List[str]
    bot_type: str = "Azure SQL Integrated Bot"
    resources: List[dict] = []


# Инициализация FastAPI
app = FastAPI(
    title="Foster Family Resource Bot Testing API",
    description="API для тестирования модулей чат-бота для семей с приемными детьми",
    version="1.0.0"
)

# CORS middleware для Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация компонентов
bot = ResourceChatBot()
classifier = QueryClassifier(bot.llm)
db_searcher = DatabaseSearcher(bot.db_searcher.connection_string)
web_searcher = WebSearcher()
url_searcher = URLSearcher()


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Foster Family Resource Bot Testing API",
        "version": "1.0.0",
        "endpoints": {
            "classify": "/classify",
            "database_search": "/database-search", 
            "web_search": "/web-search",
            "url_search": "/url-search",
            "full_bot": "/full-bot"
        }
    }


@app.post("/classify", response_model=ClassificationResponse)
async def classify_query(request: ClassificationRequest):
    """
    Тестирование LLM классификатора
    
    Пример запроса:
    {
        "query": "I need food assistance for my foster children in Austin, Texas"
    }
    """
    try:
        result = await classifier.classify(request.query)
        
        return ClassificationResponse(
            query_type=result.query_type.value,
            confidence=result.confidence,
            keywords=result.extracted_keywords,
            location_needed=result.location_needed,
            location_info=result.location_info.model_dump() if result.location_info else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")


@app.post("/database-search", response_model=List[ResourceResponse])
async def database_search(request: DatabaseSearchRequest):
    """
    Тестирование поиска в базе данных Azure SQL с векторной поддержкой
    
    Пример запроса:
    {
        "keywords": ["food", "assistance", "foster", "children"]
    }
    """
    try:
        resources = await db_searcher.search(request.keywords)
        
        return [
            ResourceResponse(
                title=resource.title,
                description=resource.description,
                category=resource.category,
                source=resource.source,
                relevance_score=resource.relevance_score,
                location=resource.location,
                url=resource.url,
                contact_info=resource.contact_info
            )
            for resource in resources
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database search error: {str(e)}")


@app.post("/web-search", response_model=List[ResourceResponse])
async def web_search(request: WebSearchRequest):
    """
    Тестирование веб-поиска
    
    Пример запроса:
    {
        "keywords": ["mental health", "foster families"],
        "location": "Austin, Texas"
    }
    """
    try:
        resources = await web_searcher.search(request.keywords, request.location)
        
        return [
            ResourceResponse(
                title=resource.title,
                description=resource.description,
                category=resource.category,
                source=resource.source,
                relevance_score=resource.relevance_score,
                location=resource.location
            )
            for resource in resources
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Web search error: {str(e)}")


@app.post("/url-search", response_model=List[ResourceResponse])
async def url_search(request: URLSearchRequest):
    """
    Тестирование поиска по URL
    
    Пример запроса:
    {
        "url": "https://fostercare.gov",
        "keywords": ["housing", "resources"]
    }
    """
    try:
        resources = await url_searcher.search(request.url, request.keywords)
        
        return [
            ResourceResponse(
                title=resource.title,
                description=resource.description,
                category=resource.category,
                source=resource.source,
                relevance_score=resource.relevance_score,
                location=resource.location
            )
            for resource in resources
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL search error: {str(e)}")


@app.post("/full-bot")
async def full_bot(request: FullBotRequest):
    """Полный flow бота с отслеживанием этапов"""
    try:
        query = request.user_input
        print(f"🤖 Полный flow для запроса: {query}")
        
        # Используем новый метод, который возвращает и ответ, и ресурсы
        result = await bot.process_user_query_with_resources(query)
        
        # Проверяем, есть ли interrupt
        if result.get("interrupt"):
            return {
                "success": True,
                "query": query,
                "response": result["response"],
                "interrupt": True,
                "interrupt_type": "location_request",
                "message": result["response"],
                "bot_type": "Azure SQL Integrated Bot"
            }
        
        # Получаем детали из состояния (если доступны)
        flow_steps = [
            "Классификация запроса",
            "Проверка локации" if "needs_location" in str(result["response"]) else None,
            "Уточнение локации" if "location" in str(result["response"]) else None,
            "Поиск ресурсов",
            "Генерация ответа"
        ]
        flow_steps = [step for step in flow_steps if step]
        
        # Определяем тип запроса и нужность локации на основе классификации
        classification = await bot.classifier.classify(query)
        
        return {
            "success": True,
            "query": query,
            "response": result["response"],
            "query_type": classification.query_type.value,
            "needs_location": classification.location_needed,
            "location": f"{classification.location_info.city}, {classification.location_info.state}" if classification.location_info else "Не указана",
            "keywords": classification.extracted_keywords,
            "flow_steps": flow_steps,
            "resources": result["resources"],
            "bot_type": "Azure SQL Integrated Bot",
            "interrupt": False
        }
        
    except Exception as e:
        print(f"❌ Ошибка в full-bot: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": request.user_input,
            "response": "Произошла ошибка при обработке запроса",
            "flow_steps": ["Ошибка"],
            "bot_type": "Azure SQL Integrated Bot",
            "interrupt": False
        }


@app.post("/location-response", response_model=LocationResponseResponse)
async def location_response(request: LocationResponseRequest):
    """Обработка ответа с локацией от пользователя"""
    try:
        print(f"📍 Processing location response: {request.location} for query: {request.original_query}")
        
        # Парсим локацию
        location_parts = request.location.split(",")
        city = location_parts[0].strip()
        state = location_parts[1].strip() if len(location_parts) > 1 else None
        
        # Классифицируем оригинальный запрос
        classification = await bot.classifier.classify(request.original_query)
        
        # Определяем тип поиска и выполняем его напрямую
        if classification.query_type.value == "database_search":
            print(f"🗄️ Searching database for {classification.extracted_keywords} in {request.location}")
            resources = await bot.db_searcher.search(classification.extracted_keywords)
            
            # Используем _format_response для генерации правильного ответа
            from agent_lito.data_types import LocationInfo
            location_info = LocationInfo(city=city, state=state)
            response = bot._format_response(resources, classification.query_type, location_info)
            
        else:
            # Для других типов поиска используем веб-поиск
            print(f"🌐 Searching web for {classification.extracted_keywords} in {request.location}")
            resources = await bot.web_searcher.search(classification.extracted_keywords, request.location)
            response = f"Found {len(resources)} web resources for foster families in {request.location}."
        
        # Преобразуем ресурсы в формат для API
        api_resources = []
        for resource in resources:
            api_resources.append({
                "title": resource.title,
                "description": resource.description,
                "category": resource.category,
                "source": "Database Search" if classification.query_type.value == "database_search" else "Web Search",
                "relevance_score": getattr(resource, 'relevance_score', 0.0),
                "location": resource.location,
                "url": resource.url,
                "contact_info": resource.contact_info
            })
        
        return {
            "success": True,
            "response": response,
            "query_type": classification.query_type.value,
            "location": request.location,
            "keywords": classification.extracted_keywords,
            "bot_type": "Azure SQL Integrated Bot",
            "resources": api_resources
        }
        
    except Exception as e:
        print(f"❌ Ошибка в location-response: {e}")
        return {
            "success": False,
            "response": f"Произошла ошибка при обработке локации: {str(e)}",
            "query_type": "error",
            "location": request.location,
            "keywords": [],
            "bot_type": "Azure SQL Integrated Bot",
            "resources": []
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 