---
name: Database Tool
description: Manage PostgreSQL and MySQL database connections with automatic SSH tunnel support. Discovers DB_* environments from ~/.secrets, executes queries, inspects schemas. Use for all database operations including querying, schema inspection, and connection testing.
allowed-tools: Bash, Read, Grep, BashOutput, KillShell
---

# Database Tool

This skill provides utilities for managing database connections with automatic SSH tunnel support for PostgreSQL and MySQL databases.

## Core Capabilities

1. **Environment Discovery**: Auto-discover all DB\_\* environments from ~/.secrets
2. **Connection Testing**: Test database connectivity with automatic tunnel setup
3. **Query Execution**: Execute SQL queries with automatic connection management
4. **Schema Inspection**: Retrieve database schema, tables, columns, and indexes
5. **SSH Tunnel Management**: Transparent SSH tunnel creation and cleanup

## When to Use This Skill

Invoke this skill when you need to:

- Discover available database environments
- Test database connections
- Execute SQL queries on PostgreSQL or MySQL
- Inspect database schemas, tables, or columns
- Work with databases behind SSH tunnels
- Manage multiple database environments (dev, staging, prod)

## Prerequisites

**Required Environment Variables in ~/.secrets:**

Database environments must follow the pattern `DB_<PROJECT>_<ENV>` with JSON configuration:

```bash
DB_ALTA_DEV='{"type":"postgres","host":"10.43.71.101","port":5432,"user":"postgres","password":"pass","database":"altadb","sslmode":"disable","ssh":{"host":"91.98.128.210","port":22,"user":"dbtunnel","key":"~/.ssh/id_rsa"}}'
```

**Required Fields:**

- `type`: Database type (`postgres` or `mysql`)
- `host`: Database host
- `user`: Database user
- `database`: Database name

**Optional Fields:**

- `port`: Database port (default: 5432 for postgres, 3306 for mysql)
- `password`: Database password
- `sslmode`: SSL mode for PostgreSQL (default: prefer)
- `ssh`: SSH tunnel configuration object (optional)
  - `host`: SSH server hostname
  - `port`: SSH port (default: 22)
  - `user`: SSH username
  - `key`: Path to SSH private key

**Required Python Packages:**

```bash
pip3 install sshtunnel psycopg2-binary mysql-connector-python
```

See `scripts/README.md` for installation details.

## Finding the Plugin Location

**IMPORTANT**: Before using this skill's scripts, locate the db-tool wrapper.

**Method 1: Auto-discover (works with any marketplace name)**

```bash
DB_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/db-tool/db-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)
```

**Method 2: Direct lookup (faster, requires knowing marketplace name)**

```bash
DB_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/db-tool/db-tool.sh
```

All commands below use `$DB_TOOL` as the entry point.

## Quick Command Reference

All commands are invoked via the `db-tool.sh` wrapper script.

### 1. Discover Available Databases

```bash
"$DB_TOOL" discover
```

Returns JSON array of all discovered DB\_\* environments with type, host, database, and SSH tunnel status.

**Example Output:**

```json
[
  {
    "env": "ALTA_DEV",
    "env_var": "DB_ALTA_DEV",
    "type": "postgres",
    "host": "10.43.71.101",
    "database": "altadb",
    "user": "postgres",
    "has_ssh_tunnel": true
  }
]
```

### 2. Test Connection

```bash
"$DB_TOOL" connect <ENV>
```

Tests database connection and returns connection details with database version.

**Example:**

```bash
"$DB_TOOL" connect ALTA_DEV
```

**Output:**

```json
{
  "status": "success",
  "env": "ALTA_DEV",
  "type": "postgres",
  "host": "10.43.71.101",
  "port": 5432,
  "database": "altadb",
  "user": "postgres",
  "ssh_tunnel": true,
  "version": "PostgreSQL 14.5..."
}
```

### 3. Execute SQL Query

```bash
"$DB_TOOL" query <ENV> <SQL>

echo "SELECT ..." | "$DB_TOOL" query <ENV> -
```

Executes SQL query with automatic SSH tunnel and connection management.

**Examples:**

```bash
"$DB_TOOL" query ALTA_DEV "SELECT * FROM users LIMIT 5"

echo "SELECT COUNT(*) FROM orders WHERE created_at > NOW() - INTERVAL '7 days'" | "$DB_TOOL" query ALTA_DEV -

cat query.sql | "$DB_TOOL" query ALTA_DEV -
```

**SELECT Output:**

```json
{
  "status": "success",
  "columns": ["id", "name", "email"],
  "rows": [
    { "id": 1, "name": "Alice", "email": "alice@example.com" },
    { "id": 2, "name": "Bob", "email": "bob@example.com" }
  ],
  "row_count": 2
}
```

**INSERT/UPDATE/DELETE Output:**

```json
{
  "status": "success",
  "affected_rows": 5
}
```

### 4. Inspect Schema

```bash
"$DB_TOOL" schema <ENV> [table]
```

Without table name: Lists all tables in the database.
With table name: Shows detailed schema for the specific table.

**Examples:**

```bash
"$DB_TOOL" schema ALTA_DEV

"$DB_TOOL" schema ALTA_DEV users
```

**List Tables Output:**

```json
{
  "status": "success",
  "env": "ALTA_DEV",
  "type": "postgres",
  "tables": ["users", "orders", "products"]
}
```

**Table Details Output:**

```json
{
  "status": "success",
  "env": "ALTA_DEV",
  "type": "postgres",
  "table": "users",
  "columns": [
    {
      "column_name": "id",
      "data_type": "integer",
      "is_nullable": "NO",
      "column_default": "nextval('users_id_seq'::regclass)",
      "character_maximum_length": null
    }
  ],
  "indexes": [
    {
      "index_name": "users_pkey",
      "definition": "CREATE UNIQUE INDEX users_pkey ON users USING btree (id)"
    }
  ]
}
```

## Complete Workflow Examples

### Discover and Connect

```bash
DB_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/db-tool/db-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

DATABASES=$("$DB_TOOL" discover)
echo "$DATABASES" | jq -r '.[].env'

"$DB_TOOL" connect ALTA_DEV
```

### Execute Query and Parse Results

```bash
RESULT=$("$DB_TOOL" query ALTA_DEV "SELECT id, name FROM users WHERE active = true")

echo "$RESULT" | jq -r '.rows[] | "\(.id): \(.name)"'
```

### Inspect Schema

```bash
TABLES=$("$DB_TOOL" schema ALTA_DEV)
echo "$TABLES" | jq -r '.tables[]'

SCHEMA=$("$DB_TOOL" schema ALTA_DEV users)
echo "$SCHEMA" | jq -r '.columns[] | "\(.column_name): \(.data_type)"'
```

## SSH Tunnel Behavior

**Automatic Management:**

- SSH tunnel is created automatically when needed
- Tunnel is closed after operation completes
- No manual tunnel management required
- Transparent to the user

**Connection Flow:**

1. Parse DB\_\* environment variable
2. If SSH config present, create SSH tunnel
3. Connect to database (via tunnel or direct)
4. Execute operation
5. Close database connection
6. Close SSH tunnel (if used)

## Additional Documentation

- **[commands.md](commands.md)** - Detailed command reference with parameters and error codes
- **[scripts/README.md](scripts/README.md)** - Installation guide and Python package requirements

## Integration with dbadmin Agent

This skill is designed to work seamlessly with the `dbadmin` agent:

1. Agent uses `discover` to show available databases
2. Agent uses `query` for all SQL execution
3. Agent uses `schema` for schema inspection
4. All operations use automatic SSH tunnel management
5. Results are returned in JSON for easy parsing

## Key Points

✅ **Auto SSH Tunnels** - Transparent tunnel creation and cleanup
✅ **Multiple Environments** - Support for dev/staging/prod via DB*\* pattern
✅ **JSON Configuration** - Single environment variable per database
✅ **Automatic Discovery** - Find all DB*\* environments from ~/.secrets
✅ **PostgreSQL & MySQL** - Support for both database types
✅ **Clean Output** - All commands return structured JSON

---

**For detailed command documentation, see [commands.md](commands.md)**
**For installation instructions, see [scripts/README.md](scripts/README.md)**
