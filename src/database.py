"""Database connection and query execution layer."""

import logging
import sqlite3
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages database connections and query execution."""

    def __init__(
        self,
        url: str = None,
        min_connections: int = 2,
        max_connections: int = 10,
        timeout: int = 5,
    ):
        """Initialize database connection.

        Args:
            url: Database connection URL (sqlite:///path/to/db.db)
                Defaults to sqlite:///database_agent.db
            min_connections: Ignored for SQLite (kept for API compatibility)
            max_connections: Ignored for SQLite (kept for API compatibility)
            timeout: Connection timeout in seconds
        """
        if url is None:
            url = os.getenv("DATABASE_URL", "sqlite:///database_agent.db")
        
        self.url = url
        self.timeout = timeout
        self.db_path = self._parse_sqlite_path(url)
        
        # Ensure database file exists
        self._initialize_database()
        logger.info(f"Database initialized at {self.db_path}")

    def _parse_sqlite_path(self, url: str) -> str:
        """Parse SQLite path from connection URL.
        
        Args:
            url: Connection URL like sqlite:///path/to/db.db
            
        Returns:
            Path to database file
        """
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "")
        elif url.startswith("sqlite://"):
            return url.replace("sqlite://", "")
        else:
            return url

    def _initialize_database(self) -> None:
        """Initialize SQLite database and create directory if needed."""
        # Create directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Create database file if it doesn't exist
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            conn.close()
            logger.info(f"Created new SQLite database at {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections.

        Yields:
            SQLite database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.timeout)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

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
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                # Convert sqlite3.Row objects to dictionaries
                result_list = [dict(row) for row in results]
                logger.info(f"Query executed successfully, returned {len(result_list)} rows")
                cursor.close()
                return result_list
            except sqlite3.Error as e:
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
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                affected = cursor.rowcount
                logger.info(f"Update executed, {affected} rows affected")
                cursor.close()
                return affected
            except sqlite3.Error as e:
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
        query = f"PRAGMA table_info({table_name})"
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                columns = cursor.fetchall()
                
                # Convert PRAGMA results to our format
                result = {
                    "table": table_name,
                    "columns": [
                        {
                            "column_name": col[1],
                            "data_type": col[2],
                            "is_nullable": "YES" if col[3] == 0 else "NO",
                        }
                        for col in columns
                    ],
                }
                cursor.close()
                return result
            except sqlite3.Error as e:
                logger.error(f"Failed to get table info: {e}")
                raise

    def get_all_tables(self) -> List[str]:
        """Get list of all accessible tables.

        Returns:
            List of table names
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                tables = cursor.fetchall()
                result = [table[0] for table in tables]
                cursor.close()
                return result
            except sqlite3.Error as e:
                logger.error(f"Failed to get tables: {e}")
                raise

    def close(self) -> None:
        """Close database connection."""
        # SQLite connections are closed in the context manager
        logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
