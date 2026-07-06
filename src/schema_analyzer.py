"""Database schema analysis and discovery."""

import logging
from typing import Dict, List, Any
from src.database import DatabaseConnection

logger = logging.getLogger(__name__)


class SchemaAnalyzer:
    """Analyzes and caches database schema information."""

    def __init__(self, db: DatabaseConnection):
        """Initialize schema analyzer.

        Args:
            db: Database connection instance
        """
        self.db = db
        self._schema_cache: Dict[str, Any] = {}
        self._cache_loaded = False

    def get_schema(self, refresh: bool = False) -> Dict[str, Any]:
        """Get complete database schema.

        Args:
            refresh: Force refresh of cache

        Returns:
            Dictionary with schema information
        """
        if self._cache_loaded and not refresh:
            return self._schema_cache

        try:
            tables = self.db.get_all_tables()
            schema = {}

            for table in tables:
                schema[table] = self.db.get_table_info(table)

            self._schema_cache = {
                "tables": schema,
                "table_count": len(tables),
            }
            self._cache_loaded = True
            logger.info(f"Schema loaded: {len(tables)} tables")
            return self._schema_cache

        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise

    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get columns for a specific table.

        Args:
            table_name: Name of the table

        Returns:
            List of column information
        """
        schema = self.get_schema()
        if table_name in schema["tables"]:
            return schema["tables"][table_name]["columns"]
        return []

    def get_table_names(self) -> List[str]:
        """Get list of all table names.

        Returns:
            List of table names
        """
        schema = self.get_schema()
        return list(schema["tables"].keys())

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in schema.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists
        """
        return table_name in self.get_table_names()

    def format_schema_for_prompt(self) -> str:
        """Format schema as text for LLM prompts.

        Returns:
            Formatted schema description
        """
        schema = self.get_schema()
        lines = ["Database Schema:"]
        lines.append("="*50)

        for table_name, table_info in schema["tables"].items():
            lines.append(f"\nTable: {table_name}")
            lines.append("-" * 30)
            for col in table_info["columns"]:
                nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
                lines.append(f"  {col['column_name']}: {col['data_type']} {nullable}")

        return "\n".join(lines)

    def clear_cache(self) -> None:
        """Clear schema cache."""
        self._schema_cache = {}
        self._cache_loaded = False
        logger.info("Schema cache cleared")
