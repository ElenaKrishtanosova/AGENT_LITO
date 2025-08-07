#!/usr/bin/env python3
"""
Архитектура LangGraph для Foster Family Resource Bot
Обновленная версия с узлом уточнения локации
"""

def get_architecture_graph():
    """Возвращает Mermaid граф архитектуры"""
    return """
graph TD
    A[User Input] --> B[classify_query_node]
    
    B --> C{Query Type?}
    
    C -->|DATABASE_SEARCH| D{Needs Location?}
    C -->|WEB_SEARCH| D
    C -->|URL_SEARCH| D
    C -->|UNCLEAR_QUERY| E[handle_unclear_node]
    
    D -->|Yes & No Location| F[check_location_node]
    D -->|No or Has Location| G{Search Type?}
    
    F --> B
    F --> H[location_response_node]
    
    G -->|DATABASE_SEARCH| I[search_database_node]
    G -->|WEB_SEARCH| J[search_web_node]
    G -->|URL_SEARCH| K[search_url_node]
    
    H --> L[generate_response_node]
    I --> L
    J --> L
    K --> L
    E --> L
    
    L --> M[Final Response]
    
    %% Стили узлов
    classDef startNode fill:#e1f5fe
    classDef classifyNode fill:#f3e5f5
    classDef locationNode fill:#fff3e0
    classDef searchNode fill:#e8f5e8
    classDef responseNode fill:#fce4ec
    classDef unclearNode fill:#ffebee
    
    class A,M startNode
    class B,C classifyNode
    class F,H locationNode
    class I,J,K searchNode
    class L responseNode
    class E unclearNode
    """

def get_architecture_description():
    """Возвращает описание архитектуры"""
    return """
# 🏗️ Архитектура Foster Family Resource Bot

## 📊 Flow графа:

### 1. **Входная точка**
- `User Input` → Пользовательский запрос

### 2. **Классификация**
- `classify_query_node` → LLM классификация запроса
- Определяет тип запроса и нужность локации

### 3. **Маршрутизация**
- **DATABASE_SEARCH** → Поиск в базе данных
- **WEB_SEARCH** → Поиск в интернете  
- **URL_SEARCH** → Поиск по конкретной ссылке
- **UNCLEAR_QUERY** → Обработка неясных запросов

### 4. **Уточнение локации** ⭐ **НОВОЕ**
- `check_location_node` → Проверка и запрос локации
- `location_response_node` → Обработка ответа с локацией
- Если нужна локация, но её нет → возврат к классификации
- После получения локации → прямой переход к поиску

### 5. **Поиск ресурсов**
- `search_database_node` → Поиск в Azure SQL
- `search_web_node` → Поиск через Tavily API
- `search_url_node` → Парсинг конкретной ссылки

### 6. **Генерация ответа**
- `generate_response_node` → Формирование финального ответа
- `Final Response` → Ответ пользователю

## 🔄 Динамическая навигация:

### **Сценарий 1: Запрос с локацией**
```
User Input → classify_query → search_database → generate_response → Final Response
```

### **Сценарий 2: Запрос без локации**
```
User Input → classify_query → check_location → location_response → generate_response → Final Response
```

### **Сценарий 3: Неясный запрос**
```
User Input → classify_query → handle_unclear → generate_response → Final Response
```

## 🎯 Ключевые особенности:

1. **LLM-классификация** - интеллектуальное определение типа запроса
2. **Уточнение локации** - обработка через location_response_node
3. **Динамическая навигация** - Command-based routing
4. **Модульная архитектура** - разделение ответственности
5. **Graceful fallback** - обработка ошибок и неясных запросов

## 🛠️ Технический стек:

- **LangGraph** - оркестрация workflow
- **LangChain** - интеграция с LLM
- **OpenAI GPT-4o-mini** - классификация и генерация
- **Azure SQL** - векторный поиск
- **Tavily API** - веб-поиск
- **FastAPI** - REST API
- **Streamlit** - UI для тестирования
"""

def print_architecture():
    """Выводит архитектуру в консоль"""
    print("🏗️ Архитектура Foster Family Resource Bot")
    print("=" * 60)
    print(get_architecture_description())
    print("\n📊 Mermaid Graph:")
    print("=" * 60)
    print(get_architecture_graph())

if __name__ == "__main__":
    print_architecture() 