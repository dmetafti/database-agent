"""Tests for database agent."""

import pytest
from src.agent import DatabaseAgent, QueryResult


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
            ],
        }


@pytest.fixture
def mock_db():
    """Create a mock database."""
    return MockDB()


@pytest.fixture
def agent(mock_db):
    """Create a database agent for testing."""
    return DatabaseAgent(mock_db)


class TestDatabaseAgent:
    """Test suite for DatabaseAgent class."""

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.db is not None
        assert agent.schema is not None
        assert agent.validator is not None

    def test_query_execution(self, agent):
        """Test basic query execution."""
        result = agent.query("Show all users")
        assert isinstance(result, QueryResult)

    def test_get_schema(self, agent):
        """Test schema retrieval."""
        schema = agent.get_schema()
        assert schema is not None

    def test_get_schema_as_text(self, agent):
        """Test schema retrieval as formatted text."""
        schema_text = agent.get_schema(as_text=True)
        assert isinstance(schema_text, str)
        assert "Database Schema" in schema_text

    def test_refresh_schema(self, agent):
        """Test schema refresh."""
        agent.refresh_schema()
        assert True
