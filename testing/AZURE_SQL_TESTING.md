# 🗄️ Azure SQL Integration Testing Guide

## 🚀 Quick Start

1. **Запуск тестового окружения:**
   ```bash
   cd /home/user/AGENT_LITO
   uv run python testing/start_testing.py
   ```

2. **Доступные URL:**
   - **UI**: http://localhost:8501
   - **API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

## 🧪 Тестирование Azure SQL Интеграции

### 1. **Database Search Testing**
- Перейдите в секцию "Database Search" в UI
- Введите ключевые слова для поиска
- Нажмите "Search Azure SQL Database"
- Проверьте результаты в таблице

**Примеры запросов:**
- `food, assistance, foster, children`
- `clothing, supplies, free`
- `childcare, daycare`
- `mental, health, therapy`
- `medical, care, children`

### 2. **Full Bot Testing**
- Перейдите в секцию "Full Bot" в UI
- Введите запрос на русском или английском
- Нажмите "Test Full Bot"
- Проверьте:
  - ✅ Классификацию запроса
  - ✅ Уточнение локации
  - ✅ Поиск в Azure SQL
  - ✅ Генерацию ответа

**Примеры запросов:**
- `Найди ресурсы для приемных семей по питанию`
- `Ищу помощь с одеждой для приемных детей`
- `Нужна медицинская помощь для приемного ребенка`
- `I need food assistance for my foster children in Austin, Texas`

### 3. **API Testing**
Прямое тестирование API:

```bash
# Поиск в базе данных
curl -X POST "http://localhost:8000/database-search" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["food", "assistance"]}'

# Полный бот
curl -X POST "http://localhost:8000/full-bot" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Найди ресурсы для приемных семей по питанию"}'
```

## 🔍 Что Проверяется

### ✅ **Классификация Запросов**
- LLM правильно определяет тип запроса
- Извлекаются ключевые слова
- Определяется нужность локации

### ✅ **Уточнение Локации**
- Если локация не указана, система запрашивает её
- Локация правильно форматируется для поиска

### ✅ **Azure SQL Поиск**
- Генерация эмбеддингов через OpenAI API
- Векторный поиск в Azure SQL
- Возврат реальных ресурсов из базы данных

### ✅ **Форматирование Результатов**
- Отображение названия, описания, категории
- Показ URL и контактной информации
- Отображение релевантности (similarity score)

## 📊 Ожидаемые Результаты

### Database Search Results:
- **Title**: Название ресурса
- **Description**: Описание услуги
- **Category**: Категория (Food, Money, Housing, etc.)
- **Location**: Локация (STATE CA, CITY Austin, etc.)
- **Website**: URL ресурса
- **Contact**: Контактная информация
- **Relevance**: Оценка релевантности (0.0-1.0)

### Full Bot Response:
- Полный ответ с найденными ресурсами
- Информация о классификации запроса
- Детали flow выполнения
- Информация о боте (Azure SQL Integrated)

## 🛠️ Технические Детали

- **Database**: Azure SQL with Vector Support
- **Vector Model**: text-embedding-3-small (1536 dimensions)
- **Similarity**: Cosine distance
- **Results**: Top 10 most similar resources
- **Threshold**: 0.3 (configurable)

## 🐛 Troubleshooting

### Если API не отвечает:
```bash
# Проверьте процессы
ps aux | grep uvicorn
ps aux | grep streamlit

# Перезапустите
pkill -f uvicorn
pkill -f streamlit
uv run python testing/start_testing.py
```

### Если нет результатов поиска:
- Проверьте подключение к Azure SQL
- Убедитесь, что CONN_STRING в .env
- Проверьте OpenAI API ключ
- Попробуйте другие ключевые слова

## 🎯 Успешное Тестирование

✅ **Все компоненты работают:**
- Классификация запросов
- Уточнение локации  
- Azure SQL векторный поиск
- Отображение результатов в UI
- Полный LangGraph workflow 