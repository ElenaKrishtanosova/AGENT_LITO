"""
LangGraph чат-бот для поиска ресурсов
"""

# Загрузка переменных окружения
from dotenv import load_dotenv
load_dotenv()

# Публичный API
from .bot import ResourceChatBot
from .data_types import QueryType, ChatState, ClassificationResult, ResourceItem
from .classification import QueryClassifier
from .search import DatabaseSearcher, WebSearcher, URLSearcher

__version__ = "0.1.0"
__all__ = [
    "ResourceChatBot",
    "QueryType", 
    "ChatState",
    "ClassificationResult",
    "ResourceItem",
    "QueryClassifier",
    "DatabaseSearcher",
    "WebSearcher", 
    "URLSearcher"
] 