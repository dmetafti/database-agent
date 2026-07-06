# Database Agent

A production-ready Python database agent that uses natural language processing to interact with SQL databases safely and efficiently.

## What This Is

Database Agent is an intelligent SQL assistant that:
- **Parses natural language queries** and converts them to SQL
- **Executes queries safely** with built-in validation and sandboxing
- **Discovers database schemas** automatically
- **Prevents SQL injection** and dangerous operations
- **Provides CLI and programmatic interfaces** for easy integration

## Features

✅ Natural language to SQL conversion
✅ Automatic schema discovery
✅ SQL injection prevention
✅ Query validation and safety checks
✅ Connection pooling and performance optimization
✅ Comprehensive logging and debugging
✅ CLI and Python API
✅ Docker support
✅ Full test coverage
✅ Production-ready error handling

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL (or MySQL/SQLite for testing)
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/dmetafti/database-agent.git
cd database-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
```

### Usage

```bash
# Interactive mode
python -m cli.main --interactive

# Single query
python -m cli.main --query "Show all users"

# View schema
python -m cli.main --schema
```

## Testing

```bash
pytest
```

## License

MIT License
