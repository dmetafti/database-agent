"""Integration tests for database agent."""

import pytest
from src.agent import DatabaseAgent, QueryResult


class MockDB:
    """Mock database for integration testing."""
    
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
def agent():
    """Create a database agent for testing."""
    return DatabaseAgent(MockDB())


class TestIntegration:
    """Integration test suite."""

    def test_full_query_pipeline(self, agent):
        """Test complete query execution pipeline."""
        result = agent.query("Count all users")
        assert isinstance(result, QueryResult)

    def test_invalid_query_handling(self, agent):
        """Test handling of invalid queries."""
        result = agent.query("DROP TABLE users")
        assert not result.success
        assert result.error is not None

    def test_schema_discovery(self, agent):
        """Test schema discovery process."""
        schema = agent.get_schema()
        assert schema is not None
        assert "tables" in schema
