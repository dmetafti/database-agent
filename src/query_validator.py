"""SQL query validation and safety checks."""

import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)


class QueryValidator:
    """Validates SQL queries for safety and compliance."""

    # Dangerous SQL keywords that should never be used
    DANGEROUS_KEYWORDS = {
        "DROP",
        "TRUNCATE",
        "ALTER",
        "CREATE",
        "DELETE",
        "UPDATE",
        "GRANT",
        "REVOKE",
    }

    # Keywords allowed for SELECT queries
    SAFE_KEYWORDS = {
        "SELECT",
        "FROM",
        "WHERE",
        "AND",
        "OR",
        "NOT",
        "IN",
        "LIKE",
        "BETWEEN",
        "JOIN",
        "INNER",
        "LEFT",
        "RIGHT",
        "FULL",
        "ON",
        "GROUP",
        "BY",
        "HAVING",
        "ORDER",
        "ASC",
        "DESC",
        "LIMIT",
        "OFFSET",
        "AS",
        "DISTINCT",
        "COUNT",
        "SUM",
        "AVG",
        "MIN",
        "MAX",
    }

    def __init__(self, allowed_tables: List[str] = None):
        """Initialize validator.

        Args:
            allowed_tables: List of tables that can be queried
        """
        self.allowed_tables = allowed_tables or []

    def validate(self, query: str) -> Tuple[bool, str]:
        """Validate a SQL query.

        Args:
            query: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for dangerous keywords
        dangerous_found = self._check_dangerous_keywords(query)
        if dangerous_found:
            return False, f"Query contains dangerous keyword: {dangerous_found}"

        # Check for SQL injection patterns
        injection_risk = self._check_sql_injection(query)
        if injection_risk:
            return False, f"Potential SQL injection detected: {injection_risk}"

        # Check for uncommented semicolons (multiple statements)
        if self._has_multiple_statements(query):
            return False, "Multiple SQL statements not allowed"

        # Check for allowed tables if specified
        if self.allowed_tables:
            unauthorized_tables = self._check_table_access(query)
            if unauthorized_tables:
                return False, f"Access denied to tables: {unauthorized_tables}"

        logger.info("Query validation passed")
        return True, ""

    def _check_dangerous_keywords(self, query: str) -> str:
        """Check for dangerous SQL keywords."""
        keywords = re.findall(r"\b\w+\b", query.upper())
        for keyword in keywords:
            if keyword in self.DANGEROUS_KEYWORDS:
                logger.warning(f"Dangerous keyword detected: {keyword}")
                return keyword
        return ""

    def _check_sql_injection(self, query: str) -> str:
        """Check for common SQL injection patterns."""
        patterns = [
            r"'\s*or\s*'1'\s*=\s*'1",
            r"--\s*$",
            r"/\*.*?\*/",
            r"xp_",
            r"sp_",
        ]

        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Potential injection pattern detected: {pattern}")
                return pattern

        return ""

    def _has_multiple_statements(self, query: str) -> bool:
        """Check if query contains multiple statements."""
        cleaned = re.sub(r"'([^']*)'|\"([^\"]*)\"", "", query)
        semicolons = len([c for c in cleaned if c == ";"])
        return semicolons > 1

    def _check_table_access(self, query: str) -> List[str]:
        """Check if query accesses unauthorized tables."""
        from_pattern = r"FROM\s+(\w+)"
        join_pattern = r"JOIN\s+(\w+)"

        tables_found = []
        tables_found.extend(re.findall(from_pattern, query, re.IGNORECASE))
        tables_found.extend(re.findall(join_pattern, query, re.IGNORECASE))

        unauthorized = []
        for table in tables_found:
            if table.upper() not in [t.upper() for t in self.allowed_tables]:
                unauthorized.append(table)

        return unauthorized
