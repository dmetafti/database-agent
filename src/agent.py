"""Main database agent implementation."""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from src.database import DatabaseConnection
from src.query_validator import QueryValidator
from src.schema_analyzer import SchemaAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of a database query."""

    success: bool
    data: List[Dict[str, Any]]
    sql: str
    error: Optional[str] = None
    rows_affected: int = 0
    execution_time: float = 0.0

    def __str__(self) -> str:
        if self.success:
            return f"Success: {len(self.data)} rows returned\nSQL: {self.sql}"
        return f"Error: {self.error}"


class DatabaseAgent:
    """Main agent for interacting with databases using natural language."""

    def __init__(
        self,
        db: DatabaseConnection,
        allowed_tables: Optional[List[str]] = None,
    ):
        """Initialize the database agent.

        Args:
            db: Database connection instance
            allowed_tables: List of tables that can be queried (None = all tables)
        """
        self.db = db
        self.schema = SchemaAnalyzer(db)
        self.validator = QueryValidator(allowed_tables or self.schema.get_table_names())
        logger.info("Database agent initialized")

    def query(self, natural_language_query: str) -> QueryResult:
        """Execute a natural language query.

        Args:
            natural_language_query: User's query in natural language

        Returns:
            QueryResult with results and generated SQL
        """
        try:
            # Generate SQL from natural language
            sql = self._generate_sql(natural_language_query)
            logger.info(f"Generated SQL: {sql}")

            # Validate the SQL
            is_valid, error_msg = self.validator.validate(sql)
            if not is_valid:
                return QueryResult(
                    success=False,
                    data=[],
                    sql=sql,
                    error=error_msg,
                )

            # Execute the query
            results = self.db.execute_query(sql)
            return QueryResult(
                success=True,
                data=results,
                sql=sql,
                rows_affected=len(results),
            )

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return QueryResult(
                success=False,
                data=[],
                sql="",
                error=str(e),
            )

    def _generate_sql(self, natural_language_query: str) -> str:
        """Generate SQL from natural language query.

        This is a simplified implementation. In production, you would use:
        - LLMs (GPT, Claude, etc.)
        - Semantic understanding
        - Template-based generation

        Args:
            natural_language_query: Natural language query

        Returns:
            Generated SQL query
        """
        schema_info = self.schema.format_schema_for_prompt()

        logger.info(f"Processing query: {natural_language_query}")

        # Simple heuristic-based conversion for demo
        if "count" in natural_language_query.lower():
            table = self._extract_table_name(natural_language_query)
            if table:
                return f"SELECT COUNT(*) as count FROM {table}"

        if "show" in natural_language_query.lower() or "get" in natural_language_query.lower():
            table = self._extract_table_name(natural_language_query)
            if table:
                return f"SELECT * FROM {table} LIMIT 10"

        # Fallback: return all from first table
        tables = self.schema.get_table_names()
        if tables:
            return f"SELECT * FROM {tables[0]} LIMIT 10"

        raise ValueError("Could not generate SQL from query")

    def _extract_table_name(self, query: str) -> Optional[str]:
        """Extract table name from natural language query.

        Args:
            query: Natural language query

        Returns:
            Table name if found
        """
        available_tables = self.schema.get_table_names()
        query_lower = query.lower()

        for table in available_tables:
            if table.lower() in query_lower:
                return table

        return None

    def get_schema(self, as_text: bool = False) -> Dict[str, Any] | str:
        """Get database schema.

        Args:
            as_text: Return as formatted text instead of dict

        Returns:
            Schema information
        """
        if as_text:
            return self.schema.format_schema_for_prompt()
        return self.schema.get_schema()

    def refresh_schema(self) -> None:
        """Refresh cached schema information."""
        self.schema.clear_cache()
        logger.info("Schema refreshed")
