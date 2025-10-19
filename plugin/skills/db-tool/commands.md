# Database Tool - Command Reference

Detailed reference for all db-tool commands.

## Command Overview

| Command    | Purpose                      | Arguments        | Stdin    |
| ---------- | ---------------------------- | ---------------- | -------- |
| `discover` | List all DB\_\* environments | None             | No       |
| `connect`  | Test database connection     | `<env>`          | No       |
| `query`    | Execute SQL query            | `<env> <sql\|->` | Optional |
| `schema`   | Inspect database schema      | `<env> [table]`  | No       |

## Command Details

### discover

**Description**: Auto-discover all DB\_\* environment variables from ~/.secrets

**Usage**:

```bash
db-tool.sh discover
```

**Arguments**: None

**Output**: JSON array of database environments

**Output Schema**:

```json
[
  {
    "env": "string",
    "env_var": "string",
    "type": "string",
    "host": "string",
    "database": "string",
    "user": "string",
    "has_ssh_tunnel": boolean
  }
]
```

**Exit Codes**:

- `0`: Success
- `1`: No DB\_\* environments found

**Example**:

```bash
DB_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/db-tool/db-tool.sh

"$DB_TOOL" discover
```

**Example Output**:

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
  },
  {
    "env": "MYAPP_PROD",
    "env_var": "DB_MYAPP_PROD",
    "type": "mysql",
    "host": "192.168.1.50",
    "database": "production",
    "user": "produser",
    "has_ssh_tunnel": false
  }
]
```

---

### connect

**Description**: Test database connection and retrieve version information

**Usage**:

```bash
db-tool.sh connect <ENV>
```

**Arguments**:

- `<ENV>`: Environment name (e.g., `ALTA_DEV`, not `DB_ALTA_DEV`)

**Output**: JSON object with connection details

**Output Schema**:

```json
{
  "status": "success|error",
  "env": "string",
  "type": "string",
  "host": "string",
  "port": number,
  "database": "string",
  "user": "string",
  "ssh_tunnel": boolean,
  "version": "string"
}
```

**Error Output Schema**:

```json
{
  "status": "error",
  "env": "string",
  "error": "string"
}
```

**Exit Codes**:

- `0`: Connection successful
- `1`: Connection failed or environment not found

**Example**:

```bash
"$DB_TOOL" connect ALTA_DEV
```

**Example Success Output**:

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
  "version": "PostgreSQL 14.5 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 4.8.5, 64-bit"
}
```

**Example Error Output**:

```json
{
  "status": "error",
  "env": "ALTA_DEV",
  "error": "could not connect to server: Connection refused"
}
```

---

### query

**Description**: Execute SQL query on specified database environment

**Usage**:

```bash
db-tool.sh query <ENV> <SQL>
db-tool.sh query <ENV> -

echo "SELECT ..." | db-tool.sh query <ENV> -
cat query.sql | db-tool.sh query <ENV> -
```

**Arguments**:

- `<ENV>`: Environment name (e.g., `ALTA_DEV`)
- `<SQL>`: SQL query string, or `-` to read from stdin

**Stdin**: SQL query (when using `-`)

**Output**: JSON object with query results or affected rows

**SELECT Output Schema**:

```json
{
  "status": "success",
  "columns": ["string"],
  "rows": [
    {
      "column_name": "value"
    }
  ],
  "row_count": number
}
```

**INSERT/UPDATE/DELETE Output Schema**:

```json
{
  "status": "success",
  "affected_rows": number
}
```

**Error Output Schema**:

```json
{
  "status": "error",
  "error": "string",
  "sql": "string"
}
```

**Exit Codes**:

- `0`: Query executed successfully
- `1`: Query failed or syntax error

**Examples**:

**Simple SELECT**:

```bash
"$DB_TOOL" query ALTA_DEV "SELECT id, name, email FROM users WHERE active = true LIMIT 5"
```

**Multi-line query via stdin**:

```bash
echo "SELECT
  u.id,
  u.name,
  COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 0" | "$DB_TOOL" query ALTA_DEV -
```

**Query from file**:

```bash
cat /path/to/query.sql | "$DB_TOOL" query ALTA_DEV -
```

**INSERT with affected rows**:

```bash
"$DB_TOOL" query ALTA_DEV "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')"
```

**Example SELECT Output**:

```json
{
  "status": "success",
  "columns": ["id", "name", "email"],
  "rows": [
    {
      "id": 1,
      "name": "Alice",
      "email": "alice@example.com"
    },
    {
      "id": 2,
      "name": "Bob",
      "email": "bob@example.com"
    }
  ],
  "row_count": 2
}
```

**Example INSERT Output**:

```json
{
  "status": "success",
  "affected_rows": 1
}
```

**Example Error Output**:

```json
{
  "status": "error",
  "error": "syntax error at or near \"SELEC\"",
  "sql": "SELEC * FROM users"
}
```

---

### schema

**Description**: Inspect database schema - list all tables or show detailed schema for specific table

**Usage**:

```bash
db-tool.sh schema <ENV>
db-tool.sh schema <ENV> <TABLE>
```

**Arguments**:

- `<ENV>`: Environment name (e.g., `ALTA_DEV`)
- `<TABLE>`: Optional table name for detailed schema

**Output**: JSON object with table list or table details

**List Tables Output Schema**:

```json
{
  "status": "success",
  "env": "string",
  "type": "string",
  "tables": ["string"]
}
```

**Table Details Output Schema (PostgreSQL)**:

```json
{
  "status": "success",
  "env": "string",
  "type": "postgres",
  "table": "string",
  "columns": [
    {
      "column_name": "string",
      "data_type": "string",
      "is_nullable": "YES|NO",
      "column_default": "string|null",
      "character_maximum_length": number|null
    }
  ],
  "indexes": [
    {
      "index_name": "string",
      "definition": "string"
    }
  ]
}
```

**Table Details Output Schema (MySQL)**:

```json
{
  "status": "success",
  "env": "string",
  "type": "mysql",
  "table": "string",
  "columns": [
    {
      "column_name": "string",
      "data_type": "string",
      "is_nullable": "YES|NO",
      "key": "PRI|MUL|UNI|",
      "column_default": "string|null",
      "extra": "string"
    }
  ],
  "indexes": [
    {
      "table": "string",
      "non_unique": number,
      "key_name": "string",
      "seq_in_index": number,
      "column_name": "string"
    }
  ]
}
```

**Error Output Schema**:

```json
{
  "status": "error",
  "error": "string"
}
```

**Exit Codes**:

- `0`: Schema retrieved successfully
- `1`: Schema retrieval failed

**Examples**:

**List all tables**:

```bash
"$DB_TOOL" schema ALTA_DEV
```

**Show table details**:

```bash
"$DB_TOOL" schema ALTA_DEV users
```

**Example List Tables Output**:

```json
{
  "status": "success",
  "env": "ALTA_DEV",
  "type": "postgres",
  "tables": ["users", "orders", "products", "categories"]
}
```

**Example Table Details Output (PostgreSQL)**:

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
    },
    {
      "column_name": "name",
      "data_type": "character varying",
      "is_nullable": "NO",
      "column_default": null,
      "character_maximum_length": 255
    },
    {
      "column_name": "email",
      "data_type": "character varying",
      "is_nullable": "NO",
      "column_default": null,
      "character_maximum_length": 255
    },
    {
      "column_name": "created_at",
      "data_type": "timestamp without time zone",
      "is_nullable": "YES",
      "column_default": "CURRENT_TIMESTAMP",
      "character_maximum_length": null
    }
  ],
  "indexes": [
    {
      "index_name": "users_pkey",
      "definition": "CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id)"
    },
    {
      "index_name": "users_email_idx",
      "definition": "CREATE UNIQUE INDEX users_email_idx ON public.users USING btree (email)"
    }
  ]
}
```

---

## Environment Variable Format

All database configurations must be stored in `~/.secrets` following this pattern:

```bash
DB_<PROJECT>_<ENV>='<JSON_CONFIG>'
```

**JSON Configuration Schema**:

```json
{
  "type": "postgres|mysql",
  "host": "string",
  "port": number,
  "user": "string",
  "password": "string",
  "database": "string",
  "sslmode": "disable|prefer|require",
  "ssh": {
    "host": "string",
    "port": number,
    "user": "string",
    "key": "string"
  }
}
```

**Required Fields**:

- `type`: Database type (`postgres` or `mysql`)
- `host`: Database server hostname/IP
- `user`: Database username
- `database`: Database name

**Optional Fields**:

- `port`: Database port (default: 5432 for postgres, 3306 for mysql)
- `password`: Database password (default: empty string)
- `sslmode`: SSL mode for PostgreSQL (default: `prefer`)
- `ssh`: SSH tunnel configuration (omit for direct connections)
  - `host`: SSH server hostname/IP
  - `port`: SSH server port (default: 22)
  - `user`: SSH username
  - `key`: Path to SSH private key file (supports `~` expansion)

**Examples**:

**PostgreSQL with SSH tunnel**:

```bash
export DB_ALTA_DEV='{"type":"postgres","host":"10.43.71.101","port":5432,"user":"postgres","password":"secret","database":"altadb","sslmode":"disable","ssh":{"host":"91.98.128.210","port":22,"user":"dbtunnel","key":"~/.ssh/id_rsa"}}'
```

**MySQL direct connection**:

```bash
export DB_MYAPP_PROD='{"type":"mysql","host":"mysql.example.com","port":3306,"user":"produser","password":"prodpass","database":"production"}'
```

**PostgreSQL direct connection (minimal)**:

```bash
export DB_TEST_LOCAL='{"type":"postgres","host":"localhost","user":"testuser","database":"testdb"}'
```

---

## Error Handling

All commands return JSON with a `status` field:

- `success`: Operation completed successfully
- `error`: Operation failed, see `error` field for details

**Common Errors**:

1. **Environment not found**:

   ```json
   {
     "error": "DB_INVALID_ENV environment variable not found"
   }
   ```

2. **Invalid JSON configuration**:

   ```json
   {
     "error": "Invalid JSON in DB_ALTA_DEV: ..."
   }
   ```

3. **Missing required field**:

   ```json
   {
     "error": "Missing required field 'database' in DB_ALTA_DEV"
   }
   ```

4. **SSH key not found**:

   ```json
   {
     "error": "SSH key not found at /Users/user/.ssh/id_rsa"
   }
   ```

5. **Connection refused**:

   ```json
   {
     "error": "could not connect to server: Connection refused"
   }
   ```

6. **SQL syntax error**:
   ```json
   {
     "error": "syntax error at or near \"FROM\"",
     "sql": "SELECT * FORM users"
   }
   ```

---

## SSH Tunnel Details

**Automatic Lifecycle**:

1. Parse environment configuration
2. If `ssh` object present, create SSH tunnel
3. Forward remote database port to local random port
4. Connect to database via `127.0.0.1:<local_port>`
5. Execute operation
6. Close database connection
7. Stop SSH tunnel

**SSH Key Authentication**:

- Only key-based authentication is supported
- Password authentication is not supported
- Key path supports tilde (`~`) expansion
- Key must be readable by current user

**Tunnel Behavior**:

- New tunnel created for each operation
- Tunnel automatically closed after operation
- No persistent tunnel state
- Random local port assigned by OS

---

## Performance Considerations

**Query Execution**:

- Each command creates a new connection
- SSH tunnel setup adds ~1-2 seconds overhead
- For multiple queries, consider combining into single query
- Use transactions for multiple write operations

**Connection Pooling**:

- Not implemented (each operation = new connection)
- Suitable for infrequent operations
- Not suitable for high-frequency queries

**Large Result Sets**:

- All results loaded into memory
- No streaming support
- Consider LIMIT clauses for large tables

---

## Integration Examples

**Parse results with jq**:

```bash
"$DB_TOOL" query ALTA_DEV "SELECT id, name FROM users" | jq -r '.rows[] | "\(.id): \(.name)"'
```

**Check connection before query**:

```bash
if "$DB_TOOL" connect ALTA_DEV | jq -e '.status == "success"' > /dev/null; then
  "$DB_TOOL" query ALTA_DEV "SELECT COUNT(*) FROM users"
else
  echo "Connection failed"
fi
```

**Iterate over discovered databases**:

```bash
"$DB_TOOL" discover | jq -r '.[].env' | while read env; do
  echo "Testing $env..."
  "$DB_TOOL" connect "$env"
done
```

**Extract specific columns**:

```bash
"$DB_TOOL" query ALTA_DEV "SELECT * FROM users LIMIT 5" | jq '.rows[] | {id, email}'
```
