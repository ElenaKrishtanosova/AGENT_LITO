"""
Быстрый тест LLM-классификации
"""

import asyncio
import os
from agent_lito import ResourceChatBot


async def quick_test():
    """Быстрый тест нескольких запросов"""
    
    print("🧪 Быстрый тест LLM-классификации")
    print("=" * 50)
    
    # Проверяем наличие API ключа
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY не найден!")
        print("Добавьте его в .env файл или переменные окружения")
        return
    
    bot = ResourceChatBot()
    
    # Тестовые запросы для каждого типа
    test_queries = [
        "Найди в базе данных книги по машинному обучению",  # DATABASE_SEARCH
        "Где можно купить iPhone в Москве?",                # WEB_SEARCH  
        "Найди информацию на сайте https://python.org",     # URL_SEARCH
        "Хочу что-то интересное"                            # UNCLEAR_QUERY
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Тестирую: '{query}'")
        print("-" * 40)
        
        try:
            result = await bot._classify_query(query)
            print(f"✅ Успешно классифицировано как: {result.query_type}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print(f"\n{'='*50}")
    print("Тест завершен!")


if __name__ == "__main__":
    asyncio.run(quick_test()) 