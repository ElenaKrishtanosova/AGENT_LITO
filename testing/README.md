# 🤖 Foster Family Resource Bot Testing

Тестирование модулей чат-бота для семей с приемными детьми через FastAPI и Streamlit UI.

## 🚀 Быстрый старт

### 1. Запуск API сервера
```bash
cd /home/user/AGENT_LITO
uv run python testing/api.py
```

API будет доступен по адресу: http://localhost:8000

### 2. Запуск Streamlit UI
```bash
# В новом терминале
cd /home/user/AGENT_LITO
uv run streamlit run testing/ui.py
```

UI будет доступен по адресу: http://localhost:8501

## 📋 Доступные эндпоинты

### 🔍 Classification Testing
- **URL**: `POST /classify`
- **Описание**: Тестирование LLM классификатора запросов
- **Пример запроса**:
```json
{
    "query": "I need food assistance for my foster children in Austin, Texas"
}
```

### 🗄️ Database Search Testing
- **URL**: `POST /database-search`
- **Описание**: Тестирование поиска в Azure SQL базе данных
- **Пример запроса**:
```json
{
    "keywords": ["food", "assistance", "foster", "children"]
}
```

### 🌐 Web Search Testing
- **URL**: `POST /web-search`
- **Описание**: Тестирование веб-поиска через внешние API
- **Пример запроса**:
```json
{
    "keywords": ["mental health", "foster families"],
    "location": "Austin, Texas"
}
```

### 🔗 URL Search Testing
- **URL**: `POST /url-search`
- **Описание**: Тестирование поиска по конкретному URL
- **Пример запроса**:
```json
{
    "url": "https://fostercare.gov",
    "keywords": ["housing", "resources"]
}
```

### 🤖 Full Bot Testing
- **URL**: `POST /full-bot`
- **Описание**: Тестирование полного бота с LangGraph
- **Пример запроса**:
```json
{
    "user_input": "I need food assistance for my foster children in Austin, Texas"
}
```

## 🧪 Тестовые сценарии

### Classification Testing
1. **DATABASE_SEARCH**: "I need food assistance for my foster children in Austin, Texas"
2. **WEB_SEARCH**: "Where can I find mental health resources for foster families online?"
3. **URL_SEARCH**: "Check this website https://fostercare.gov for housing resources"
4. **UNCLEAR_QUERY**: "I just need some help"

### Database Search Testing
1. **Food Resources**: ["food", "assistance", "foster", "children"]
2. **Clothing Resources**: ["clothing", "supplies", "free"]
3. **Childcare Resources**: ["childcare", "daycare"]
4. **Mental Health**: ["mental", "health", "therapy"]

### Web Search Testing
1. **Mental Health**: ["mental health", "foster families"] + "Austin, Texas"
2. **Food Assistance**: ["food assistance", "foster families"] + "Travis County"
3. **Childcare**: ["childcare resources", "foster families"] + "Austin"

### URL Search Testing
1. **Foster Care Gov**: "https://fostercare.gov" + ["housing", "resources"]
2. **Adopt US Kids**: "https://adoptuskids.org" + ["support", "services"]

## 📊 Ожидаемые результаты

### Classification
- **Query Type**: DATABASE_SEARCH, WEB_SEARCH, URL_SEARCH, UNCLEAR_QUERY
- **Confidence**: 0.0 - 1.0 (высокая для четких запросов)
- **Keywords**: Извлеченные ключевые слова
- **Location**: Автоматически извлеченная локация

### Resources
- **Title**: Название ресурса
- **Description**: Описание ресурса
- **Category**: Категория (Food, Clothing/Supplies, Mental Health, etc.)
- **Source**: Источник (database, web, url)
- **Relevance**: Релевантность (0.0 - 1.0)
- **Location**: Локация ресурса

## 🔧 Troubleshooting

### API не запускается
```bash
# Проверьте зависимости
uv sync

# Проверьте переменные окружения
echo $OPENAI_API_KEY
```

### UI не подключается к API
```bash
# Проверьте, что API запущен
curl http://localhost:8000/

# Проверьте порты
netstat -tlnp | grep :8000
```

### Ошибки классификации
- Проверьте OpenAI API ключ
- Убедитесь, что модель доступна (gpt-4o-mini)
- Проверьте лимиты API

## 📝 Логи

API логи выводятся в консоль:
```
🔍 Classifying query: I need food assistance for my foster children in Austin, Texas
🤖 LLM Classification:
   Type: QueryType.DATABASE_SEARCH
   Confidence: 0.95
   Keywords: ['food assistance', 'foster children']
   Location needed: False
   Location: city='Austin' county='' state='Texas'
```

## 🎯 Цель тестирования

Этот интерфейс предназначен для:
- ✅ **Демонстрации заказчику** работы каждого модуля
- ✅ **Тестирования LLM классификации** на различных запросах
- ✅ **Проверки поисковых модулей** с разными параметрами
- ✅ **Валидации полного бота** в реальных сценариях
- ✅ **Отладки и оптимизации** перед production 