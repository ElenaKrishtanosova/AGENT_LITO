"""
Azure SQL database search with vector support
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
    """Azure SQL database searcher for foster family resources"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Search constants
        self.TOP_N = 10
        self.MIN_COSINE = 0.3  # Lowered from 0.7 to get more results
        # Hybrid weighted sum: alpha*vector + (1-alpha)*keyword
        self.HYBRID_ALPHA = 0.65
    
    async def search(self, keywords: List[str]) -> List[ResourceItem]:
        """
        Execute hybrid search (vector + keyword) in Azure SQL
        """
        print("🗄️ Searching database for foster family resources (hybrid)")
        
        try:
            # Combine keywords into the search query
            search_query = " ".join(keywords)
            print(f"   Search query: {search_query}")
            
            # Generate embeddings
            embedding = await self._generate_embeddings(search_query)
            if not embedding:
                print("   Error: Could not generate embeddings")
                return []
            
            # Execute hybrid search
            results = await self._execute_hybrid_search(search_query, embedding)
            
            # If hybrid returns no results, fallback to vector-only
            if not results:
                print("   No hybrid results, falling back to vector-only...")
                results = await self._execute_vector_search(search_query, embedding)
            
            # Convert results to ResourceItem
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
        Generates embeddings for text using OpenAI API
        
        Args:
            text: Text to vectorize
            
        Returns:
            List of float values for the embedding or None on error
        """
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            
            # Get the embedding from the response
            embedding = response.data[0].embedding
            
            # Convert to string for SQL
            embedding_str = json.dumps(embedding)
            
            print(f"   Generated embedding with {len(embedding)} dimensions")
            return embedding_str
            
        except Exception as e:
            print(f"   Error generating embeddings: {e}")
            return None
    
    async def _execute_vector_search(self, query: str, embedding: str) -> List[dict]:
        """
        Executes vector search in Azure SQL
        
        Args:
            query: Original text query
            embedding: JSON string with embedding
            
        Returns:
            List of search results
        """
        try:
            # Create SQL query with vector search
            sql_query = self._build_vector_query(embedding)
            print(f"   SQL Query: {sql_query[:200]}...")
            
            # Execute query
            results = await self._execute_query(sql_query)
            
            # If no results, try without similarity filter
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
        Creates SQL query with vector search for Azure SQL
        
        Args:
            embedding: JSON string with embedding
            
        Returns:
            SQL query with VECTOR_DISTANCE
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
        Executes SQL query to Azure SQL
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            List of results as dictionaries
        """
        try:
            # Use asyncio for non-blocking execution
            loop = asyncio.get_event_loop()
            
            def execute_sync():
                with pyodbc.connect(self.connection_string) as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql_query)
                    
                    # Get column names
                    columns = [column[0] for column in cursor.description]
                    
                    # Get results
                    rows = cursor.fetchall()
                    
                    # Convert to list of dictionaries
                    results = []
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        results.append(row_dict)
                    
                    return results
            
            # Execute in a separate thread
            results = await loop.run_in_executor(None, execute_sync)
            
            print(f"   Executed query, got {len(results)} results")
            return results
            
        except Exception as e:
            print(f"   Error executing query: {e}")
            return [] 

    def _build_hybrid_query(self, embedding: str, keywords_text: str) -> str:
        """
        Builds a hybrid query, combining vector similarity and full-text score.
        Requires a configured FULLTEXT INDEX on text columns (e.g., description, resource_name).
        """
        # Example based on Azure SQL hybrid search approaches:
        # Final score: alpha*vector + (1-alpha)*keyword_score
        # For keyword_score, we use FREETEXTTABLE/CONTAINSTABLE (normalize rank)
        alpha = self.HYBRID_ALPHA
        return f"""
        DECLARE @v1 VECTOR(1536) = '{embedding}';
        DECLARE @alpha FLOAT = {alpha};
        
        -- Full-text score via FREETEXTTABLE on multiple columns
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
        Executes a hybrid (vector + keyword) query
        """
        try:
            sql_query = self._build_hybrid_query(embedding, keywords_text.replace("'", "''"))
            print(f"   HYBRID SQL: {sql_query[:200]}...")
            results = await self._execute_query(sql_query)
            return results
        except Exception as e:
            print(f"   Error executing hybrid search: {e}")
            return [] 