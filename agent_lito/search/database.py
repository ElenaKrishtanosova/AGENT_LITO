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
        # Гибридная взвешенная сумма: alpha*vector + (1-alpha)*keyword
        self.HYBRID_ALPHA = 0.65
    
    async def search(self, keywords: List[str]) -> List[ResourceItem]:
        """
        Выполняет гибридный поиск (векторный + ключевые слова) в Azure SQL
        """
        print("🗄️ Searching database for foster family resources (hybrid)")
        
        try:
            # Объединяем ключевые слова в поисковый запрос
            search_query = " ".join(keywords)
            print(f"   Search query: {search_query}")
            
            # Генерируем эмбеддинги
            embedding = await self._generate_embeddings(search_query)
            if not embedding:
                print("   Error: Could not generate embeddings")
                return []
            
            # Выполняем гибридный поиск
            results = await self._execute_hybrid_search(search_query, embedding)
            
            # Если гибрид не дал результатов, fallback на чистый вектор
            if not results:
                print("   No hybrid results, falling back to vector-only...")
                results = await self._execute_vector_search(search_query, embedding)
            
            # Преобразуем результаты в ResourceItem
            resources = []
            for result in results:
                category = result.get('service_category', 'General')
                if category and ',' in category:
                    category = category.split(',')[0].strip()
                location = result.get('area_served', 'Location not specified')
                if location and location.startswith('COUNTY '):
                    location = location.replace('COUNTY ', '')
                url = result.get('resource_url') or result.get('org_url')
                contact_info = result.get('org_name')
                resource = ResourceItem(
                    title=result.get('resource_name', 'Unknown Resource'),
                    description=result.get('description', 'No description available'),
                    category=category,
                    source="database",
                    relevance_score=result.get('hybrid_score') or result.get('similarity_score', 0.0),
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

    def _build_hybrid_query(self, embedding: str, keywords_text: str) -> str:
        """
        Строит гибридный запрос, комбинируя векторную близость и полнотекстовый скор.
        Требует настроенного FULLTEXT INDEX по текстовым колонкам (например, description, resource_name).
        """
        # Пример на основе подходов из Azure SQL hybrid search:
        # Итоговый скор: alpha*vector + (1-alpha)*keyword_score
        # Для keyword_score используем FREETEXTTABLE/CONTAINSTABLE (нормализуем ранг)
        alpha = self.HYBRID_ALPHA
        return f"""
        DECLARE @v1 VECTOR(1536) = '{embedding}';
        DECLARE @alpha FLOAT = {alpha};
        
        -- Полнотекстовый скор через FREETEXTTABLE по нескольким колонкам
        WITH kw AS (
            SELECT k.[KEY] as RMS_id, CAST(k.RANK AS FLOAT) / 1000.0 AS kw_score
            FROM FREETEXTTABLE(rms.rms_table_view, (description, resource_name, service_category, profile_category), '{keywords_text}') k
        )
        SELECT TOP {self.TOP_N}
            t.RMS_id,
            t.description,
            t.resource_name,
            t.org_name,
            t.org_url,
            t.resource_url,
            t.area_served,
            t.service_category,
            t.profile_category,
            (1 - VECTOR_DISTANCE('cosine', @v1, t.VectorBinary)) AS vector_score,
            ISNULL(kw.kw_score, 0.0) AS kw_score,
            (@alpha * (1 - VECTOR_DISTANCE('cosine', @v1, t.VectorBinary)) + (1-@alpha) * ISNULL(kw.kw_score, 0.0)) AS hybrid_score
        FROM rms.rms_table_view t
        LEFT JOIN kw ON kw.RMS_id = t.RMS_id
        ORDER BY hybrid_score DESC;"""

    async def _execute_hybrid_search(self, keywords_text: str, embedding: str) -> List[dict]:
        """
        Выполняет гибридный (vector + keyword) запрос
        """
        try:
            sql_query = self._build_hybrid_query(embedding, keywords_text.replace("'", "''"))
            print(f"   HYBRID SQL: {sql_query[:200]}...")
            results = await self._execute_query(sql_query)
            return results
        except Exception as e:
            print(f"   Error executing hybrid search: {e}")
            return [] 