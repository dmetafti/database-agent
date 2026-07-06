"""Tests for query validator."""

import pytest
from src.query_validator import QueryValidator


class TestQueryValidator:
    """Test suite for QueryValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a validator for testing."""
        return QueryValidator(allowed_tables=["users", "products"])

    def test_valid_select_query(self, validator):
        """Test that valid SELECT queries pass validation."""
        query = "SELECT * FROM users WHERE id = 1"
        is_valid, error = validator.validate(query)
        assert is_valid
        assert error == ""

    def test_dangerous_drop_keyword(self, validator):
        """Test that DROP queries are rejected."""
        query = "DROP TABLE users"
        is_valid, error = validator.validate(query)
        assert not is_valid
        assert "dangerous" in error.lower()

    def test_dangerous_delete_keyword(self, validator):
        """Test that DELETE queries are rejected."""
        query = "DELETE FROM users"
        is_valid, error = validator.validate(query)
        assert not is_valid
        assert "dangerous" in error.lower()

    def test_sql_injection_pattern(self, validator):
        """Test that SQL injection patterns are detected."""
        query = "SELECT * FROM users WHERE name = 'admin' OR '1'='1'"
        is_valid, error = validator.validate(query)
        assert not is_valid

    def test_multiple_statements(self, validator):
        """Test that multiple statements are rejected."""
        query = "SELECT * FROM users; DROP TABLE users;"
        is_valid, error = validator.validate(query)
        assert not is_valid
        assert "multiple" in error.lower()

    def test_table_access_denied(self, validator):
        """Test that access to unauthorized tables is denied."""
        query = "SELECT * FROM admin_users"
        is_valid, error = validator.validate(query)
        assert not is_valid
        assert "access denied" in error.lower()
