"""PostgreSQL database client utilities"""
import os
import json
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import ThreadedConnectionPool
from shared.common.logging import logger


class DatabaseClient:
    """PostgreSQL database client"""
    
    def __init__(self, postgres_url: Optional[str] = None):
        """
        Initialize database client.
        
        Args:
            postgres_url: PostgreSQL connection URL
        """
        self.postgres_url = postgres_url or os.getenv("POSTGRES_URL", "postgresql://lolqa:lolqa_password@localhost:5432/lolqa")
        self.pool: Optional[ThreadedConnectionPool] = None
        self._init_pool()
    
    def _init_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self.postgres_url
            )
            # Test connection
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            self.pool = None
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return results.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        if not self.pool:
            return []
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> bool:
        """
        Execute INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            True if successful
        """
        if not self.pool:
            return False
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    return True
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            return False
    
    def create_pipeline_job(self, job_id: str, status: str = "queued", message: str = "") -> bool:
        """Create pipeline job record"""
        query = """
            INSERT INTO pipeline_jobs (job_id, status, message)
            VALUES (%s, %s, %s)
            ON CONFLICT (job_id) DO UPDATE
            SET status = EXCLUDED.status, message = EXCLUDED.message, updated_at = CURRENT_TIMESTAMP
        """
        return self.execute_update(query, (job_id, status, message))
    
    def update_pipeline_job(self, job_id: str, status: str, message: str = "", result: Dict = None, error: str = None) -> bool:
        """Update pipeline job record"""
        query = """
            UPDATE pipeline_jobs
            SET status = %s, message = %s, result = %s, error = %s,
                updated_at = CURRENT_TIMESTAMP,
                started_at = CASE WHEN status = 'queued' AND %s = 'running' THEN CURRENT_TIMESTAMP ELSE started_at END,
                completed_at = CASE WHEN %s IN ('completed', 'failed') THEN CURRENT_TIMESTAMP ELSE completed_at END
            WHERE job_id = %s
        """
        return self.execute_update(query, (status, message, json.dumps(result) if result else None, error, status, status, job_id))
    
    def get_pipeline_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline job by ID"""
        query = "SELECT * FROM pipeline_jobs WHERE job_id = %s"
        results = self.execute_query(query, (job_id,))
        return results[0] if results else None
    
    def log_query(self, question: str, answer: str, service: str, response_time_ms: int, metadata: Dict = None) -> bool:
        """Log query to history"""
        query = """
            INSERT INTO query_history (question, answer, service, response_time_ms, metadata)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_update(query, (question, answer, service, response_time_ms, json.dumps(metadata) if metadata else None))


# Global database client instance
_db_client: Optional[DatabaseClient] = None


def get_db_client() -> DatabaseClient:
    """Get global database client instance"""
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient()
    return _db_client

