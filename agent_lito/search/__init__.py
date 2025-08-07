"""
Поисковые модули для различных источников данных
"""

from .database import DatabaseSearcher
from .web import WebSearcher
from .url import URLSearcher

__all__ = ["DatabaseSearcher", "WebSearcher", "URLSearcher"] 