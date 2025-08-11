"""
Поиск в Azure SQL базе данных с векторной поддержкой
"""

import asyncio
import os
import json
from typing import List, Optional
import pyodbc
import numpy as np
from openai import OpenAI
from ..data_types import ResourceItem


class DatabaseSearcher:
    """Поисковик в Azure SQL базе данных для ресурсов семей с приемными детьми"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Константы для поиска
        self.TOP_N = 10
        self.MIN_COSINE = 0.3  # Lowered from 0.7 to get more results
    
    async def search(self, keywords: List[str]) -> List[ResourceItem]:
        """
        Выполняет векторный поиск в Azure SQL с векторной поддержкой
        
        Args:
            keywords: Список ключевых слов для поиска
            
        Returns:
            Список найденных ресурсов для семей с приемными детьми
        """
        print("🗄️ Searching database for foster family resources")
        
        try:
            # Объединяем ключевые слова в поисковый запрос
            search_query = " ".join(keywords)
            print(f"   Search query: {search_query}")
            
            # Генерируем эмбеддинги
            embedding = await self._generate_embeddings(search_query)
            if not embedding:
                print("   Error: Could not generate embeddings")
                return []
            
            # Выполняем векторный поиск
            results = await self._execute_vector_search(search_query, embedding)
            
            # Преобразуем результаты в ResourceItem
            resources = []
            for result in results:
                # Определяем категорию на основе service_category
                category = result.get('service_category', 'General')
                if category and ',' in category:
                    category = category.split(',')[0].strip()  # Берем первую категорию
                
                # Определяем локацию из area_served
                location = result.get('area_served', 'Location not specified')
                if location and location.startswith('COUNTY '):
                    location = location.replace('COUNTY ', '')
                
                # Определяем URL (приоритет resource_url, затем org_url)
                url = result.get('resource_url') or result.get('org_url')
                
                # Создаем контактную информацию из org_name
                contact_info = result.get('org_name')
                
                resource = ResourceItem(
                    title=result.get('resource_name', 'Unknown Resource'),
                    description=result.get('description', 'No description available'),
                    category=category,
                    source="database",
                    relevance_score=result.get('similarity_score', 0.0),
                    location=location,
                    url=url,
                    contact_info=contact_info
                )
                resources.append(resource)
            
            print(f"   Found {len(resources)} resources")
            return resources
            
        except Exception as e:
            print(f"   Error during database search: {e}")
            return []
    
    async def _generate_embeddings(self, text: str) -> Optional[List[float]]:
        """
        Генерирует эмбеддинги для текста используя OpenAI API
        
        Args:
            text: Текст для векторизации
            
        Returns:
            Список float значений эмбеддинга или None при ошибке
        """
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            
            # Получаем эмбеддинг из ответа
            embedding = response.data[0].embedding
            
            # Преобразуем в строку для SQL
            embedding_str = json.dumps(embedding)
            
            print(f"   Generated embedding with {len(embedding)} dimensions")
            return embedding_str
            
        except Exception as e:
            print(f"   Error generating embeddings: {e}")
            return None
    
    async def _execute_vector_search(self, query: str, embedding: str) -> List[dict]:
        """
        Выполняет векторный поиск в Azure SQL
        
        Args:
            query: Оригинальный текстовый запрос
            embedding: JSON строка с эмбеддингом
            
        Returns:
            Список результатов поиска
        """
        try:
            # Создаем SQL запрос с векторным поиском
            sql_query = self._build_vector_query(embedding)
            print(f"   SQL Query: {sql_query[:200]}...")
            
            # Выполняем запрос
            results = await self._execute_query(sql_query)
            
            # Если нет результатов, попробуем без фильтра по similarity
            if not results:
                print("   No results with similarity filter, trying without filter...")
                sql_query_no_filter = f"""
                DECLARE @v1 VECTOR(1536) = '{embedding}';

                SELECT TOP {self.TOP_N}
                    RMS_id,
                    description,
                    resource_name,
                    org_name,
                    org_url,
                    resource_url,
                    area_served,
                    service_category,
                    profile_category,
                    (1 - VECTOR_DISTANCE('cosine', @v1, VectorBinary)) AS similarity_score
                FROM rms.rms_table_view
                ORDER BY similarity_score DESC
                """
                results = await self._execute_query(sql_query_no_filter)
                print(f"   Results without filter: {len(results)}")
            
            return results
            
        except Exception as e:
            print(f"   Error executing vector search: {e}")
            return []
    
    def _build_vector_query(self, embedding: str) -> str:
        """
        Создает SQL-запрос с векторным поиском для Azure SQL
        
        Args:
            embedding: JSON строка с эмбеддингом
            
        Returns:
            SQL запрос с VECTOR_DISTANCE
        """
        return f"""
        DECLARE @v1 VECTOR(1536) = '{embedding}';

        SELECT TOP {self.TOP_N}
            RMS_id,
            description,
            resource_name,
            org_name,
            org_url,
            resource_url,
            area_served,
            service_category,
            profile_category,
            (1 - VECTOR_DISTANCE('cosine', @v1, VectorBinary)) AS similarity_score
        FROM rms.rms_table_view
        WHERE (1 - VECTOR_DISTANCE('cosine', @v1, VectorBinary)) > {self.MIN_COSINE}
        ORDER BY similarity_score DESC
        """
    
    async def _execute_query(self, sql_query: str) -> List[dict]:
        """
        Выполняет SQL запрос к Azure SQL
        
        Args:
            sql_query: SQL запрос для выполнения
            
        Returns:
            Список результатов в виде словарей
        """
        try:
            # Используем asyncio для неблокирующего выполнения
            loop = asyncio.get_event_loop()
            
            def execute_sync():
                with pyodbc.connect(self.connection_string) as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql_query)
                    
                    # Получаем названия колонок
                    columns = [column[0] for column in cursor.description]
                    
                    # Получаем результаты
                    rows = cursor.fetchall()
                    
                    # Преобразуем в список словарей
                    results = []
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        results.append(row_dict)
                    
                    return results
            
            # Выполняем в отдельном потоке
            results = await loop.run_in_executor(None, execute_sync)
            
            print(f"   Executed query, got {len(results)} results")
            return results
            
        except Exception as e:
            print(f"   Error executing query: {e}")
            return [] 