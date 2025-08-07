"""
Типы данных для LangGraph чат-бота
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import operator
from typing_extensions import Annotated


class QueryType(str, Enum):
    """Типы пользовательских запросов"""
    DATABASE_SEARCH = "database_search"      # Поиск ресурсов для приемных семей в БД
    WEB_SEARCH = "web_search"               # Поиск ресурсов в интернете
    URL_SEARCH = "url_search"               # Поиск по конкретной ссылке
    UNCLEAR_QUERY = "unclear_query"         # Неясный запрос


class LocationInfo(BaseModel):
    """Информация о локации пользователя"""
    city: Optional[str] = Field(default=None, description="Город")
    county: Optional[str] = Field(default=None, description="Округ/район")
    state: Optional[str] = Field(default=None, description="Штат/область")


class ClassificationResult(BaseModel):
    """Результат классификации запроса"""
    query_type: QueryType = Field(description="Тип запроса")
    confidence: float = Field(description="Уверенность в классификации (0-1)")
    extracted_keywords: List[str] = Field(description="Извлеченные ключевые слова")
    location_needed: bool = Field(description="Нужна ли локация для поиска")
    location_info: Optional[LocationInfo] = Field(default=None, description="Извлеченная информация о локации")


class ResourceItem(BaseModel):
    """Элемент найденного ресурса"""
    title: str = Field(description="Название ресурса")
    description: str = Field(description="Описание ресурса") 
    category: str = Field(description="Категория (Clothing/Supplies, Financial, Food, etc.)")
    source: str = Field(description="Источник (database, web, url)")
    relevance_score: float = Field(description="Релевантность (0-1)")
    location: Optional[str] = Field(default=None, description="Локация ресурса")
    url: Optional[str] = Field(default=None, description="URL ресурса")
    contact_info: Optional[str] = Field(default=None, description="Контактная информация")


class ChatState(BaseModel):
    """Состояние чат-бота"""
    # Основные поля
    user_input: str = Field(default="", description="Пользовательский ввод")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="История диалога")
    
    # Результаты классификации
    query_type: Optional[QueryType] = Field(default=None, description="Тип запроса")
    classification: Optional[ClassificationResult] = Field(default=None, description="Результат классификации")
    
    # Данные для поиска
    search_keywords: List[str] = Field(default_factory=list, description="Ключевые слова для поиска")
    user_location: Optional[LocationInfo] = Field(default=None, description="Локация пользователя")
    search_url: Optional[str] = Field(default=None, description="URL для поиска")
    
    # Результаты поиска
    found_resources: List[ResourceItem] = Field(default_factory=list, description="Найденные ресурсы")
    
    # Управление диалогом
    clarification_attempts: int = Field(default=0, description="Количество попыток уточнения")
    needs_location: bool = Field(default=False, description="Нужна ли локация")
    is_conversation_complete: bool = Field(default=False, description="Завершен ли диалог")
    from_location_check: bool = Field(default=False, description="Пришел ли запрос из узла уточнения локации")
    next_node: Optional[str] = Field(default=None, description="Следующий узел для выполнения")
    
    # Interrupt механизмы
    interrupt_message: Optional[str] = Field(default=None, description="Сообщение для interrupt")
    waiting_for_location: bool = Field(default=False, description="Ожидание ответа с локацией")
    original_query: Optional[str] = Field(default=None, description="Оригинальный запрос при interrupt")
    
    # Финальный ответ
    final_response: str = Field(default="", description="Финальный ответ пользователю") 