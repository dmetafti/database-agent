# Database Agent Architecture

## Overview

The Database Agent is built with a modular, layered architecture that separates concerns and enables easy testing and maintenance.

```
┌─────────────────────────────────────────┐
│          CLI / API Interface             │
├─────────────────────────────────────────┤
│      DatabaseAgent (Main Orchestrator)  │
├─────────────────────────────────────────┤
│  ┌──────────────────────────────────┐   │
│  │   Query Generation & Analysis    │   │
│  │  - Natural language processing   │   │
│  │  - SQL generation                │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│  ┌──────────────────────────────────┐   │
│  │  Validation & Safety Layer       │   │
│  │  - SQL injection detection       │   │
│  │  - Query validation              │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│  ┌──────────────────────────────────┐   │
│  │  Schema Analysis & Discovery     │   │
│  │  - Table enumeration             │   │
│  │  - Column introspection          │   │
│  │  - Caching layer                 │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│      Database Connection Layer          │
│  - Connection pooling                   │
│  - Query execution                      │
│  - Error handling                       │
├─────────────────────────────────────────┤
│           PostgreSQL / MySQL            │
└─────────────────────────────────────────┘
```

## Core Components

### 1. DatabaseAgent (agent.py)
Main orchestrator that coordinates all components.

**Responsibilities:**
- Accept natural language queries
- Delegate to appropriate components
- Return formatted results
- Manage error handling

### 2. DatabaseConnection (database.py)
Manages database connectivity and execution.

**Responsibilities:**
- Connection pooling
- Query execution
- Transaction management
- Error handling

### 3. QueryValidator (query_validator.py)
Ensures query safety before execution.

**Responsibilities:**
- Detect SQL injection attempts
- Block dangerous keywords
- Validate table access
- Check for multiple statements

### 4. SchemaAnalyzer (schema_analyzer.py)
Analyzes and caches database structure.

**Responsibilities:**
- Discover database schema
- Cache schema information
- Provide schema to other components
- Format schema for prompts

## Data Flow

### Query Execution Flow

```
User Input (Natural Language)
    ↓
DatabaseAgent.query()
    ↓
Generate SQL from natural language
    ↓
QueryValidator.validate()
    ├─ Check dangerous keywords
    ├─ Check SQL injection patterns
    ├─ Check table access
    └─ Check for multiple statements
    ↓
DatabaseConnection.execute_query()
    ├─ Get connection from pool
    ├─ Execute query
    └─ Return results
    ↓
Format and return QueryResult
```

## Security Architecture

**Defense in Depth:**
1. Input validation (QueryValidator)
2. Schema sandboxing (allowed tables)
3. Connection isolation
4. Comprehensive logging
5. Parameterized queries
