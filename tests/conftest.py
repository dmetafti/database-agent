"""Pytest configuration and fixtures."""

import pytest


class MockDB:
    """Mock database for testing."""
    
    def execute_query(self, query, params=None):
        return [{"id": 1, "name": "Test"}]

    def get_all_tables(self):
        return ["users", "products"]

    def get_table_info(self, table_name):
        return {
            "table": table_name,
            "columns": [
                {"column_name": "id", "data_type": "integer", "is_nullable": "NO"},
                {"column_name": "name", "data_type": "varchar", "is_nullable": "YES"},
            ],
        }


@pytest.fixture
def mock_db():
    """Create a mock database connection."""
    return MockDB()


@pytest.fixture
def agent(mock_db):
    """Create a database agent for testing."""
    from src.agent import DatabaseAgent
    return DatabaseAgent(mock_db)
