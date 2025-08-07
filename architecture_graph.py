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
    
    C -->|DATABASE_SEARCH| D{Location needed?}
    C -->|WEB_SEARCH| E{Location needed?}
    C -->|URL_SEARCH| F{Location needed?}
    C -->|UNCLEAR_QUERY| G[handle_unclear_node]
    
    D -->|Yes| H[check_location_node]
    D -->|No| I[search_database_node]
    E -->|Yes| H
    E -->|No| J[search_web_node]
    F -->|Yes| H
    F -->|No| K[search_url_node]
    
    H --> L{Location Available?}
    L -->|No| M[INTERRUPT: Request Location]
    L -->|Yes| N{Direct to Search Type}
    
    N -->|DATABASE_SEARCH| I
    N -->|WEB_SEARCH| J
    N -->|URL_SEARCH| K
    
    G --> O{Attempts < 2?}
    O -->|Yes| P[Request clarification]
    O -->|No| Q[End conversation]
    
    P --> B
    Q --> R[generate_response_node]
    
    I --> R
    J --> R
    K --> R
    
    R --> S[Final Response]
    
    %% Стили узлов
    classDef startNode fill:#e1f5fe
    classDef classifyNode fill:#f3e5f5
    classDef locationNode fill:#fff3e0
    classDef searchNode fill:#e8f5e8
    classDef responseNode fill:#fce4ec
    classDef unclearNode fill:#ffebee
    classDef interruptNode fill:#ffcdd2
    
    class A,S startNode
    class B,C classifyNode
    class H,L,N locationNode
    class I,J,K searchNode
    class R responseNode
    class G,O unclearNode
    class M interruptNode
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