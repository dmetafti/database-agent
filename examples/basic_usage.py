#!/usr/bin/env python3
"""Basic usage examples for the database agent."""

import sys
from src.agent import DatabaseAgent
from src.database import DatabaseConnection
from src.utils import setup_logging, load_env_file


def main():
    """Run basic examples."""
    setup_logging("INFO")

    env = load_env_file()
    db_url = env.get("DATABASE_URL") or "postgresql://localhost/test"

    try:
        print("Connecting to database...")
        db = DatabaseConnection(db_url)
        agent = DatabaseAgent(db)
        print("✅ Connected!\n")

        # Example 1: Print schema
        print("=== Database Schema ===")
        print(agent.get_schema(as_text=True))
        print()

        # Example 2: Execute a simple query
        print("=== Example Query ===")
        result = agent.query("Show all users")
        if result.success:
            print(f"SQL: {result.sql}")
            print(f"Rows: {result.rows_affected}")
            for row in result.data[:3]:
                print(f"  {row}")
        else:
            print(f"Error: {result.error}")
        print()

        # Example 3: Count query
        print("=== Count Query ===")
        result = agent.query("Count users")
        if result.success:
            print(f"SQL: {result.sql}")
            print(f"Results: {result.data}")
        else:
            print(f"Error: {result.error}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()
        print("\n✅ Done!")


if __name__ == "__main__":
    main()
