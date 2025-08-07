#!/usr/bin/env python3
"""
Главный файл для запуска Foster Family Resource Bot
"""

import asyncio
from agent_lito import ResourceChatBot
from architecture_graph import print_architecture


async def demo_classification():
    """Демонстрация классификации запросов"""
    print("🔍 Демонстрация классификации запросов")
    print("=" * 50)
    
    bot = ResourceChatBot()
    
    test_queries = [
        "I need food assistance for my foster children in Austin, Texas",
        "Where can I find mental health resources for foster families?",
        "Looking for childcare resources",
        "What's the weather like today?"  # Неясный запрос
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Запрос: {query}")
        print("-" * 40)
        
        try:
            classification = await bot.classifier.classify(query)
            print(f"   Тип: {classification.query_type}")
            print(f"   Уверенность: {classification.confidence:.2f}")
            print(f"   Ключевые слова: {classification.extracted_keywords}")
            print(f"   Нужна локация: {classification.location_needed}")
            if classification.location_info:
                print(f"   Локация: {classification.location_info}")
            else:
                print(f"   Локация: не найдена")
        except Exception as e:
            print(f"   Ошибка: {e}")


async def show_architecture():
    """Показывает архитектуру проекта"""
    print_architecture()


async def interactive_mode():
    """Интерактивный режим работы с ботом"""
    print("🤖 Интерактивный режим Foster Family Resource Bot")
    print("=" * 60)
    print("Введите запросы для тестирования. Для выхода введите 'quit'")
    print("-" * 60)
    
    bot = ResourceChatBot()
    
    while True:
        try:
            user_input = input("\n💬 Ваш запрос: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 До свидания!")
                break
            
            if not user_input:
                continue
            
            print("\n🔄 Обрабатываю запрос...")
            response = await bot.process_user_query(user_input)
            print(f"\n📝 Ответ: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")


async def test_location_flow():
    """Тестирование flow с уточнением локации"""
    print("🧪 Тестирование flow с уточнением локации")
    print("=" * 60)
    
    bot = ResourceChatBot()
    
    test_cases = [
        {
            "query": "I need food assistance for my foster children in Austin, Texas",
            "description": "Запрос с локацией - должен идти сразу в поиск"
        },
        {
            "query": "Where can I find mental health resources for foster families?",
            "description": "Запрос без локации - должен запросить локацию"
        },
        {
            "query": "Looking for childcare resources",
            "description": "Краткий запрос без локации - должен запросить локацию"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"Запрос: {test_case['query']}")
        print("-" * 50)
        
        try:
            response = await bot.process_user_query(test_case['query'])
            print(f"Ответ: {response}")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        print("-" * 50)


async def main():
    """Главная функция"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "classify":
            await demo_classification()
        elif command == "architecture":
            await show_architecture()
        elif command == "interactive":
            await interactive_mode()
        elif command == "test-location":
            await test_location_flow()
        else:
            print("❌ Неизвестная команда")
            print("Доступные команды:")
            print("  python main.py classify      - Демонстрация классификации")
            print("  python main.py architecture  - Показать архитектуру")
            print("  python main.py interactive   - Интерактивный режим")
            print("  python main.py test-location - Тестирование flow с локацией")
    else:
        # По умолчанию показываем архитектуру
        await show_architecture()


if __name__ == "__main__":
    asyncio.run(main()) 