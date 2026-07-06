# Database Agent API Reference

## DatabaseAgent

Main class for interacting with databases using natural language.

### Methods

#### query(natural_language_query: str) → QueryResult

Execute a natural language query.

```python
result = agent.query("Show me all users created in the last 30 days")
if result.success:
    print(f"SQL: {result.sql}")
    print(f"Data: {result.data}")
else:
    print(f"Error: {result.error}")
```

#### get_schema(as_text: bool = False) → Dict[str, Any] | str

Retrieve the database schema.

```python
schema_dict = agent.get_schema()
schema_text = agent.get_schema(as_text=True)
```

#### refresh_schema() → None

Refresh the cached schema.

```python
agent.refresh_schema()
```

## QueryResult

Result object returned by `agent.query()`.

### Attributes

- `success` (bool): Query executed successfully
- `data` (List[Dict]): Query results
- `sql` (str): Generated SQL query
- `error` (Optional[str]): Error message if failed
- `rows_affected` (int): Number of rows returned
- `execution_time` (float): Execution time in seconds

## DatabaseConnection

Manages database connectivity.

### Methods

#### execute_query(query: str, params: Optional[List] = None) → List[Dict]

Execute a SELECT query.

```python
results = db.execute_query(
    "SELECT * FROM users WHERE id = %s",
    [1]
)
```

#### execute_update(query: str, params: Optional[List] = None) → int

Execute INSERT/UPDATE/DELETE.

```python
affected = db.execute_update(
    "UPDATE users SET name = %s WHERE id = %s",
    ["New Name", 1]
)
```

#### get_table_info(table_name: str) → Dict

Get table metadata.

```python
info = db.get_table_info("users")
```

#### get_all_tables() → List[str]

Get list of all tables.

```python
tables = db.get_all_tables()
```

## QueryValidator

Validates SQL queries for safety.

### Methods

#### validate(query: str) → Tuple[bool, str]

Validate a SQL query.

```python
is_valid, error_msg = validator.validate("SELECT * FROM users")
```

## SchemaAnalyzer

Analyzes database schema.

### Methods

#### get_schema(refresh: bool = False) → Dict

Get database schema.

```python
schema = analyzer.get_schema()
```

#### get_table_columns(table_name: str) → List[Dict]

Get columns for a table.

```python
columns = analyzer.get_table_columns("users")
```

#### format_schema_for_prompt() → str

Format schema for LLM prompts.

```python
schema_text = analyzer.format_schema_for_prompt()
```
