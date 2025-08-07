"""
Основной модуль для демонстрации архитектуры LangGraph чат-бота
"""

import asyncio
from agent_lito import ResourceChatBot


async def main():
    """Основная функция для тестирования"""
    print("🤖 Инициализирую чат-бота...")
    bot = ResourceChatBot()
    
    # Выводим mermaid граф архитектуры
    print("\n📊 Архитектура проекта (Mermaid граф):")
    print(bot.app.get_graph().draw_mermaid())
    
    # Тестируем различные типы запросов
    test_queries = [
        "Найди в базе данных книги по искусственному интеллекту",
        "Где в интернете можно купить ноутбук в Москве?", 
        "Найди информацию на сайте https://example.com про Python",
        "Хочу что-то интересное"
    ]
    
    print("\n🧪 Тестирую различные типы запросов:")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Запрос: {query}")
        print("-" * 40)
        
        try:
            response = await bot.process_user_query(query)
            print(f"Ответ: {response}")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main()) 