"""
Тестирование LLM-классификации запросов
"""

import asyncio
import os
from agent_lito import ResourceChatBot


async def test_llm_classification():
    """Тестирование LLM классификации на различных типах запросов"""
    
    print("🧪 Тестирование LLM-классификации запросов")
    print("=" * 70)
    
    # Проверяем наличие API ключа
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY не найден в переменных окружения!")
        print("Создайте .env файл с вашим OpenAI API ключом")
        return
    
    bot = ResourceChatBot()
    
    # Расширенный набор тестовых запросов
    test_cases = [
        # DATABASE_SEARCH
        ("Найди в базе данных книги по машинному обучению", "DATABASE_SEARCH"),
        ("Поиск в БД информации о пользователях", "DATABASE_SEARCH"),
        ("Что есть в database про криптографию?", "DATABASE_SEARCH"),
        
        # WEB_SEARCH
        ("Где можно купить iPhone в Москве?", "WEB_SEARCH"),
        ("Найди рестораны японской кухни поблизости", "WEB_SEARCH"),
        ("Поиск магазинов одежды в центре города", "WEB_SEARCH"),
        ("Лучшие курсы программирования онлайн", "WEB_SEARCH"),
        
        # URL_SEARCH
        ("Найди информацию про Python на сайте https://python.org", "URL_SEARCH"),
        ("Что нового на www.github.com про LangChain?", "URL_SEARCH"),
        ("Проанализируй контент по ссылке http://example.com", "URL_SEARCH"),
        
        # UNCLEAR_QUERY
        ("Хочу что-то интересное", "UNCLEAR_QUERY"),
        ("Помоги мне", "UNCLEAR_QUERY"),
        ("Не знаю что делать", "UNCLEAR_QUERY"),
        ("Скучно", "UNCLEAR_QUERY"),
    ]
    
    results = []
    
    for i, (query, expected_type) in enumerate(test_cases, 1):
        print(f"\n{i}. Тестовый запрос: '{query}'")
        print(f"   Ожидаемый тип: {expected_type}")
        print("-" * 50)
        
        try:
            # Тестируем только классификацию
            classification = await bot._classify_query(query)
            
            # Проверяем результат
            is_correct = classification.query_type.value.upper() == expected_type
            status = "✅ ПРАВИЛЬНО" if is_correct else "❌ НЕПРАВИЛЬНО"
            
            print(f"   Результат: {status}")
            print(f"   Получен тип: {classification.query_type}")
            
            results.append({
                "query": query,
                "expected": expected_type,
                "actual": classification.query_type.value.upper(),
                "correct": is_correct,
                "confidence": classification.confidence,
                "keywords": classification.extracted_keywords,
                "location_needed": classification.location_needed
            })
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            results.append({
                "query": query,
                "expected": expected_type,
                "actual": "ERROR",
                "correct": False,
                "confidence": 0.0,
                "keywords": [],
                "location_needed": False
            })
    
    # Статистика
    print("\n" + "=" * 70)
    print("📊 СТАТИСТИКА ТЕСТИРОВАНИЯ")
    print("=" * 70)
    
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    accuracy = correct / total * 100 if total > 0 else 0
    
    print(f"Всего тестов: {total}")
    print(f"Правильных: {correct}")
    print(f"Точность: {accuracy:.1f}%")
    
    # Детальный анализ по типам
    print("\n📈 АНАЛИЗ ПО ТИПАМ ЗАПРОСОВ:")
    for query_type in ["DATABASE_SEARCH", "WEB_SEARCH", "URL_SEARCH", "UNCLEAR_QUERY"]:
        type_results = [r for r in results if r["expected"] == query_type]
        if type_results:
            type_correct = sum(1 for r in type_results if r["correct"])
            type_accuracy = type_correct / len(type_results) * 100
            print(f"  {query_type}: {type_correct}/{len(type_results)} ({type_accuracy:.1f}%)")
    
    # Примеры ошибок
    errors = [r for r in results if not r["correct"] and r["actual"] != "ERROR"]
    if errors:
        print(f"\n❌ ПРИМЕРЫ ОШИБОК КЛАССИФИКАЦИИ:")
        for error in errors[:3]:  # Показываем первые 3 ошибки
            print(f"  Запрос: '{error['query']}'")
            print(f"  Ожидалось: {error['expected']}, Получено: {error['actual']}")
    
    print("\n" + "=" * 70)
    
    return results


async def test_single_query(query: str):
    """Тест одного запроса с подробным выводом"""
    print(f"🔍 Тестирование запроса: '{query}'")
    print("-" * 50)
    
    bot = ResourceChatBot()
    
    try:
        classification = await bot._classify_query(query)
        
        print(f"📋 Результат классификации:")
        print(f"  Тип запроса: {classification.query_type}")
        print(f"  Уверенность: {classification.confidence:.2f}")
        print(f"  Ключевые слова: {classification.extracted_keywords}")
        print(f"  Нужна локация: {classification.location_needed}")
        
        return classification
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


async def main():
    """Основная функция тестирования"""
    
    print("🤖 Тестирование LLM-классификации чат-бота")
    print("Выберите режим тестирования:")
    print("1. Полное тестирование всех типов запросов")
    print("2. Тест одного запроса")
    
    choice = input("\nВведите номер (1 или 2): ").strip()
    
    if choice == "1":
        await test_llm_classification()
    elif choice == "2":
        query = input("Введите запрос для тестирования: ").strip()
        if query:
            await test_single_query(query)
        else:
            print("Запрос не может быть пустым!")
    else:
        print("Некорректный выбор!")


if __name__ == "__main__":
    asyncio.run(main()) 