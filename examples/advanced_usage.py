#!/usr/bin/env python3
"""Advanced usage patterns for the database agent."""

import sys
from src.agent import DatabaseAgent
from src.database import DatabaseConnection
from src.query_validator import QueryValidator
from src.utils import setup_logging, load_env_file


def main():
    """Run advanced examples."""
    setup_logging("DEBUG")
    env = load_env_file()
    db_url = env.get("DATABASE_URL") or "postgresql://localhost/test"

    try:
        db = DatabaseConnection(db_url)
        agent = DatabaseAgent(db)

        # Example 1: Custom validator with restricted tables
        print("=== Example 1: Restricted Table Access ===")
        restricted_agent = DatabaseAgent(
            db,
            allowed_tables=["users", "orders"],
        )
        result = restricted_agent.query("Show users")
        print(f"Result: {result}\n")

        # Example 2: Schema refresh
        print("=== Example 2: Schema Refresh ===")
        print("Initial schema:")
        initial_tables = agent.schema.get_table_names()
        print(f"Tables: {initial_tables}")
        agent.refresh_schema()
        refreshed_tables = agent.schema.get_table_names()
        print(f"After refresh: {refreshed_tables}\n")

        # Example 3: Get table info
        print("=== Example 3: Table Information ===")
        if initial_tables:
            table = initial_tables[0]
            columns = agent.schema.get_table_columns(table)
            print(f"Table '{table}' columns:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
        print()

        # Example 4: Query validation
        print("=== Example 4: Query Validation ===")
        validator = QueryValidator(allowed_tables=initial_tables)

        test_queries = [
            "SELECT * FROM users WHERE id = 1",
            "DROP TABLE users",
            "SELECT * FROM nonexistent_table",
        ]

        for query in test_queries:
            is_valid, error = validator.validate(query)
            status = "✅ Valid" if is_valid else f"❌ Invalid: {error}"
            print(f"{query}")
            print(f"  {status}\n")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()
        print("Done!")


if __name__ == "__main__":
    main()
