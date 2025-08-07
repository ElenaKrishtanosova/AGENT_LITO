# Архитектура LangGraph чат-бота для поиска ресурсов

## Обзор

Этот проект представляет собой интеллектуального чат-бота, построенного на архитектуре LangGraph с динамической навигацией. Бот способен классифицировать пользовательские запросы и направлять их в соответствующие модули для поиска ресурсов.

## Типы запросов

Система поддерживает 4 основных типа пользовательских запросов:

1. **DATABASE_SEARCH** - Поиск в базе данных Azure SQL
2. **WEB_SEARCH** - Поиск в интернете через поисковые API
3. **URL_SEARCH** - Поиск по конкретной ссылке
4. **UNCLEAR_QUERY** - Неясные запросы, требующие уточнения

## Архитектура узлов

### 1. classify_query (Узел классификации)
**Функция**: Анализирует пользовательский ввод и определяет тип запроса
**Входы**: user_input
**Выходы**: query_type, classification, search_keywords, needs_location
**Описание**: Использует LLM или эвристические правила для классификации запроса

### 2. check_location (Узел проверки локации)
**Функция**: Проверяет необходимость локации для веб-поиска или URL-поиска
**Входы**: needs_location, user_location
**Выходы**: user_location (если запрошена)
**Описание**: Запрашивает у пользователя локацию через interrupt механизм

### 3. location_response (Узел обработки ответа с локацией)
**Функция**: Обрабатывает ответ пользователя с локацией и направляет к поиску
**Входы**: user_input (локация), original_query, query_type
**Выходы**: user_location, next_node
**Описание**: Парсит локацию из ответа пользователя и направляет к соответствующему поиску
```python
def location_response(location_text: str, original_query: str) -> Command:
    """
    Обрабатывает ответ пользователя с локацией
    
    Принимает: текст локации от пользователя
    Возвращает: Command с обновленной локацией и направлением к поиску
    
    Парсит локацию и определяет следующий узел на основе типа запроса
    """
```

### 4. search_database (Узел поиска в БД)
**Функция**: Выполняет векторный поиск в Azure SQL базе данных
**Входы**: search_keywords
**Выходы**: found_resources
**Описание**: 
```python
def search_database(keywords: List[str]) -> List[ResourceItem]:
    """
    Выполняет векторный поиск в Azure SQL с векторной поддержкой
    
    Принимает: список ключевых слов
    Возвращает: список релевантных ресурсов с оценками похожести
    
    Использует SQL запрос с VECTOR_DISTANCE для поиска
    """
```

### 5. search_web (Узел веб-поиска)
**Функция**: Выполняет поиск в интернете через внешние API
**Входы**: search_keywords, user_location
**Выходы**: found_resources
**Описание**:
```python
def search_web(keywords: List[str], location: str) -> List[ResourceItem]:
    """
    Выполняет поиск в интернете через Tavily API или аналогичный сервис
    
    Принимает: ключевые слова, локация пользователя
    Возвращает: список найденных веб-ресурсов
    
    Интегрируется с поисковыми API для получения актуальной информации
    """
```

### 6. search_url (Узел поиска по URL)
**Функция**: Извлекает и анализирует контент с конкретного URL
**Входы**: search_url, search_keywords
**Выходы**: found_resources
**Описание**:
```python
def search_url(url: str, keywords: List[str]) -> List[ResourceItem]:
    """
    Парсит контент с указанного URL и ищет релевантную информацию
    
    Принимает: URL для анализа, ключевые слова для поиска
    Возвращает: релевантную информацию с сайта
    
    Использует веб-скрапинг и анализ контента
    """
```

### 7. handle_unclear (Узел обработки неясных запросов)
**Функция**: Обрабатывает неопределенные запросы и запрашивает уточнения
**Входы**: clarification_attempts
**Выходы**: user_input (уточненный) или final_response (завершение)
**Описание**:
```python
def handle_unclear(attempts: int) -> Union[str, Command]:
    """
    Обрабатывает неясные запросы с максимум 2 попытками уточнения
    
    Принимает: количество попыток уточнения
    Возвращает: либо уточненный запрос, либо вежливо завершает диалог
    
    Реализует эскалацию при невозможности понять запрос
    """
```

### 8. generate_response (Узел генерации ответа)
**Функция**: Создает финальный ответ пользователю на основе найденных ресурсов
**Входы**: found_resources, query_type
**Выходы**: final_response
**Описание**:
```python
def generate_response(resources: List[ResourceItem]) -> str:
    """
    Генерирует структурированный ответ с найденными ресурсами
    
    Принимает: список найденных ресурсов
    Возвращает: отформатированный ответ для пользователя
    
    Использует LLM для создания естественного ответа
    """
```

## Динамическая навигация

Система использует LangGraph Command API для динамической маршрутизации:

```python
# Пример динамической навигации в classify_query
if classification.query_type == QueryType.DATABASE_SEARCH:
    next_node = "search_database"
elif classification.query_type == QueryType.WEB_SEARCH:
    if classification.location_needed and not state.user_location:
        next_node = "check_location"
    else:
        next_node = "search_web"
# ... и т.д.

return Command(
    goto=next_node,
    update={"classification": classification, ...}
)
```

## Состояние системы (ChatState)

```python
class ChatState(BaseModel):
    # Основные поля
    user_input: str
    conversation_history: List[Dict[str, str]]
    
    # Результаты классификации
    query_type: Optional[QueryType]
    classification: Optional[ClassificationResult]
    
    # Данные для поиска
    search_keywords: List[str]
    user_location: Optional[str]
    search_url: Optional[str]
    
    # Результаты поиска
    found_resources: List[ResourceItem]
    
    # Управление диалогом
    clarification_attempts: int
    needs_location: bool
    is_conversation_complete: bool
    
    # Финальный ответ
    final_response: str
```

## Технологический стек

- **Ядро**: LangChain + LangGraph с динамической навигацией
- **База данных**: Azure SQL Server with Vector Support
- **LLM**: OpenAI GPT-4
- **Веб-поиск**: Tavily API (рекомендуемый)
- **Веб-скрапинг**: BeautifulSoup4 + aiohttp

## Зависимости

Основные пакеты определены в `pyproject.toml`:
- langgraph>=0.2.0
- langchain-openai>=0.1.0
- pyodbc>=5.0.0 (для Azure SQL)
- tavily-python>=0.3.0 (для веб-поиска)
- beautifulsoup4>=4.12.0 (для парсинга URL)

## Примеры использования

### 1. Поиск в базе данных
```
Пользователь: "Найди в базе данных книги по искусственному интеллекту"
Система: classify_query → search_database → generate_response
```

### 2. Веб-поиск с локацией
```
Пользователь: "Где можно купить ноутбук в Москве?"
Система: classify_query → check_location → location_response → search_web → generate_response
```

### 3. Поиск по URL
```
Пользователь: "Найди информацию про Python на сайте https://example.com"
Система: classify_query → search_url → generate_response
```

### 4. Неясный запрос
```
Пользователь: "Хочу что-то интересное"
Система: classify_query → handle_unclear → (уточнение) → classify_query → ...
```

## Интеграция с Azure SQL

```python
def get_combined_query_new(query: str) -> str:
    """
    Создает SQL-запрос с векторным поиском для Azure SQL
    """
    user_query_embedding = generate_embeddings(query)
    
    final_query = f"""
    DECLARE @v1 VECTOR(1536) = '{user_query_embedding}';

    SELECT TOP {TOP_N}
        RMS_id,
        description,
        resource_name,
        (1 - VECTOR_DISTANCE('cosine', @v1, VectorBinary)) AS similarity_score
    FROM rms.rms_table_view
    WHERE (1 - VECTOR_DISTANCE('cosine', @v1, VectorBinary)) > {MIN_COSINE}
    ORDER BY similarity_score DESC
    """
    return final_query
```

## Конфигурация

Переменные окружения в `.env`:
```
OPENAI_API_KEY=your_openai_key
CONN_STRING=your_azure_sql_connection_string
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
```

## Развертывание и масштабирование

1. **Разработка**: MemorySaver для быстрого тестирования
2. **Продакшн**: AsyncSqliteSaver для персистентности состояний
3. **Мониторинг**: Интеграция с LangSmith для отслеживания выполнения

## Следующие шаги

1. Реализация реальных интеграций (Azure SQL, Tavily API)
2. Добавление interrupt механизмов для взаимодействия с пользователем
3. Улучшение классификации запросов с помощью LLM
4. Добавление кэширования результатов поиска
5. Реализация feedback loop для улучшения релевантности 