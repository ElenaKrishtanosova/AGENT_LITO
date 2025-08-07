"""
Тест логики уточнения локации
"""

import asyncio
from agent_lito import ResourceChatBot


async def test_location_flow():
    """Тестирование flow с уточнением локации"""
    print("🧪 Тестирование логики уточнения локации")
    print("=" * 60)
    
    bot = ResourceChatBot()
    
    # Тестовые запросы
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


async def test_classification_with_location():
    """Тестирование классификации с локацией"""
    print("\n🔍 Тестирование классификации с локацией")
    print("=" * 60)
    
    bot = ResourceChatBot()
    
    # Тестируем классификацию напрямую
    queries = [
        "I need food assistance for my foster children in Austin, Texas",
        "Where can I find mental health resources for foster families?",
        "Looking for childcare resources in Los Angeles, CA"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Запрос: {query}")
        
        # Получаем классификацию
        classification = await bot.classifier.classify(query)
        
        print(f"   Тип: {classification.query_type}")
        print(f"   Уверенность: {classification.confidence:.2f}")
        print(f"   Ключевые слова: {classification.extracted_keywords}")
        print(f"   Нужна локация: {classification.location_needed}")
        if classification.location_info:
            print(f"   Локация: {classification.location_info}")
        else:
            print(f"   Локация: не найдена")


async def main():
    """Основная функция"""
    await test_location_flow()
    await test_classification_with_location()


if __name__ == "__main__":
    asyncio.run(main()) 