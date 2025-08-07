# 🚀 Быстрый старт тестирования

## Вариант 1: Автоматический запуск (рекомендуется)

```bash
cd /home/user/AGENT_LITO
uv run python testing/start_testing.py
```

Этот скрипт автоматически:
- ✅ Проверит зависимости
- ✅ Запустит API сервер
- ✅ Запустит Streamlit UI
- ✅ Откроет все необходимые URL

## Вариант 2: Ручной запуск

### Шаг 1: Запуск API
```bash
cd /home/user/AGENT_LITO
uv run python testing/api.py
```

### Шаг 2: Запуск UI (в новом терминале)
```bash
cd /home/user/AGENT_LITO
uv run streamlit run testing/ui.py
```

## 📋 Доступные URL

После запуска будут доступны:
- **🎨 UI**: http://localhost:8501
- **🔧 API**: http://localhost:8000
- **📚 API Docs**: http://localhost:8000/docs

## 🧪 Тестовые запросы

### Classification
```
"I need food assistance for my foster children in Austin, Texas"
"Where can I find mental health resources for foster families online?"
"Check this website https://fostercare.gov for housing resources"
```

### Database Search
```
["food", "assistance", "foster", "children"]
["clothing", "supplies", "free"]
["childcare", "daycare"]
```

### Web Search
```
Keywords: ["mental health", "foster families"]
Location: "Austin, Texas"
```

## 🎯 Что тестировать

1. **🔍 Classification** - LLM классификация запросов
2. **🗄️ Database Search** - Поиск в Azure SQL
3. **🌐 Web Search** - Поиск в интернете
4. **🔗 URL Search** - Поиск по конкретным сайтам
5. **🤖 Full Bot** - Полный бот с LangGraph

## 🔧 Troubleshooting

### API не запускается
```bash
# Проверьте OpenAI API ключ
echo $OPENAI_API_KEY

# Переустановите зависимости
uv sync
```

### UI не подключается
```bash
# Проверьте что API работает
curl http://localhost:8000/

# Перезапустите UI
pkill -f streamlit
uv run streamlit run testing/ui.py
```

## 📊 Ожидаемые результаты

- **Classification**: 95% confidence для четких запросов
- **Location extraction**: Автоматическое извлечение city/county/state
- **Resources**: Релевантные результаты для foster families
- **Response time**: < 3 секунды для каждого запроса 