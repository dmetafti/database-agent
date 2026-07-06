#!/usr/bin/env python3
"""Command-line interface for the database agent."""

import argparse
import logging
import os
import sys
from typing import Optional

from src.agent import DatabaseAgent
from src.database import DatabaseConnection
from src.utils import setup_logging, load_env_file

logger = logging.getLogger(__name__)


def setup_database() -> DatabaseConnection:
    """Setup database connection from environment."""
    env = load_env_file()
    db_url = env.get("DATABASE_URL") or os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError(
            "DATABASE_URL not set. Set it in .env file or as environment variable."
        )

    return DatabaseConnection(db_url)


def interactive_mode(agent: DatabaseAgent) -> None:
    """Run interactive query mode."""
    print("\n=== Database Agent Interactive Mode ===")
    print("Type 'help' for commands, 'exit' to quit\n")

    while True:
        try:
            query = input("📊 Query> ").strip()

            if not query:
                continue

            if query.lower() == "exit":
                print("Goodbye!")
                break

            if query.lower() == "help":
                print_help()
                continue

            if query.lower() == "schema":
                print(agent.get_schema(as_text=True))
                continue

            result = agent.query(query)
            print_result(result)

        except KeyboardInterrupt:
            print("\nInterrupted.")
            break
        except Exception as e:
            print(f"Error: {e}")


def print_result(result) -> None:
    """Print query result."""
    print("\n" + "="*50)
    if result.success:
        print(f"✅ Success ({result.rows_affected} rows)")
        print(f"\nSQL Generated:\n{result.sql}")
        print(f"\nResults:")
        if result.data:
            for i, row in enumerate(result.data[:10], 1):
                print(f"  {i}. {dict(row)}")
            if len(result.data) > 10:
                print(f"  ... and {len(result.data) - 10} more rows")
        else:
            print("  (No rows)")
    else:
        print(f"❌ Error: {result.error}")
        if result.sql:
            print(f"\nSQL Attempted:\n{result.sql}")
    print("="*50 + "\n")


def print_help() -> None:
    """Print help information."""
    print("""
Available Commands:
  query <text>     Execute a natural language query
  schema           Show database schema
  help             Show this help message
  exit             Quit the application

Examples:
  > Show all users
  > Count customers by country
  > Get top 10 products by revenue
    """)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Database Agent - Natural language SQL query interface"
    )
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        help="Execute a single query and exit",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Start in interactive mode",
    )
    parser.add_argument(
        "-s",
        "--schema",
        action="store_true",
        help="Print database schema and exit",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    try:
        # Setup database
        print("🔌 Connecting to database...")
        db = setup_database()
        agent = DatabaseAgent(db)
        print("✅ Connected!\n")

        # Execute based on arguments
        if args.schema:
            print(agent.get_schema(as_text=True))
        elif args.query:
            result = agent.query(args.query)
            print_result(result)
        elif args.interactive or not args.query:
            interactive_mode(agent)
        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if "db" in locals():
            db.close()
            print("\n🔌 Disconnected from database")


if __name__ == "__main__":
    main()
