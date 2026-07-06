"""Database connection and query execution layer."""

import logging
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool, Error
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages database connections and query execution."""

    def __init__(
        self,
        url: str,
        min_connections: int = 2,
        max_connections: int = 10,
        timeout: int = 5,
    ):
        """Initialize database connection pool.

        Args:
            url: Database connection URL (postgresql://user:password@host:port/db)
            min_connections: Minimum pool size
            max_connections: Maximum pool size
            timeout: Connection timeout in seconds
        """
        self.url = url
        self.timeout = timeout
        self.pool = None
        self._initialize_pool(min_connections, max_connections)
        logger.info(f"Database connection pool initialized with {min_connections}-{max_connections} connections")

    def _initialize_pool(self, min_size: int, max_size: int) -> None:
        """Initialize connection pool."""
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                min_size,
                max_size,
                self.url,
                connect_timeout=self.timeout,
            )
        except Error as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections.

        Yields:
            Database connection from pool
        """
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Error as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    def execute_query(
        self,
        query: str,
        params: Optional[List[Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results.

        Args:
            query: SQL query string
            params: Query parameters for safe parameterized queries

        Returns:
            List of dictionaries with query results
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(query, params or ())
                    results = cur.fetchall()
                    logger.info(f"Query executed successfully, returned {len(results)} rows")
                    return results
                except Error as e:
                    logger.error(f"Query execution error: {e}")
                    raise

    def execute_update(
        self,
        query: str,
        params: Optional[List[Any]] = None,
    ) -> int:
        """Execute an INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query string
            params: Query parameters for safe parameterized queries

        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(query, params or ())
                    conn.commit()
                    affected = cur.rowcount
                    logger.info(f"Update executed, {affected} rows affected")
                    return affected
                except Error as e:
                    conn.rollback()
                    logger.error(f"Update execution error: {e}")
                    raise

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table's columns and types.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with table information
        """
        query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """
        results = self.execute_query(query, [table_name])
        return {
            "table": table_name,
            "columns": results,
        }

    def get_all_tables(self) -> List[str]:
        """Get list of all accessible tables.

        Returns:
            List of table names
        """
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        results = self.execute_query(query)
        return [row["table_name"] for row in results]

    def close(self) -> None:
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Connection pool closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
