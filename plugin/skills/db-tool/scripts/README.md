# Database Tool - Scripts Documentation

Python scripts for database management with automatic SSH tunnel support.

## Prerequisites

### Required Python Packages

Install the following packages globally:

```bash
pip3 install sshtunnel psycopg2-binary mysql-connector-python
```

**Package Details:**

- **sshtunnel** (0.4.0+): SSH tunnel creation and management
- **psycopg2-binary** (2.9+): PostgreSQL database adapter
- **mysql-connector-python** (9.0+): MySQL database connector

### Verify Installation

```bash
python3 -c "import sshtunnel; import psycopg2; import mysql.connector; print('All packages installed successfully')"
```

### Python Version

- **Minimum**: Python 3.7
- **Recommended**: Python 3.9+
- **Tested**: Python 3.9, 3.10, 3.11

Check your version:

```bash
python3 --version
```

## Script Architecture

### Core Scripts

1. **db_api.py** - Core database connection manager
   - DatabaseConfig: Parses and validates DB\_\* environment variables
   - DatabaseConnection: Manages connections and SSH tunnels
   - Automatic tunnel lifecycle management
   - Context manager for safe resource cleanup

2. **discover.py** - Environment discovery
   - Scans environment for DB\_\* variables
   - Validates JSON configuration
   - Returns list of available databases

3. **connect.py** - Connection testing
   - Tests database connectivity
   - Retrieves database version
   - Verifies SSH tunnel setup

4. **query.py** - SQL query execution
   - Executes SQL queries
   - Returns structured JSON results
   - Supports stdin input

5. **schema.py** - Schema inspection
   - Lists all tables
   - Shows detailed table schema
   - Retrieves indexes and constraints

## Script Usage

All scripts are invoked via the `db-tool.sh` wrapper. Direct Python invocation is supported but not recommended.

### Direct Script Invocation (Advanced)

If you need to call scripts directly for debugging:

```bash
cd /path/to/plugin/skills/db-tool/scripts

source ~/.secrets

python3 discover.py

python3 connect.py ALTA_DEV

python3 query.py ALTA_DEV "SELECT * FROM users LIMIT 5"

echo "SELECT COUNT(*) FROM orders" | python3 query.py ALTA_DEV -

python3 schema.py ALTA_DEV

python3 schema.py ALTA_DEV users
```

## Environment Configuration

### Configuration Format

All database configurations must be JSON strings in environment variables:

```bash
DB_<PROJECT>_<ENV>='{"type":"postgres","host":"...","user":"...","database":"..."}'
```

### Required Fields

- `type`: Database type (`postgres` or `mysql`)
- `host`: Database hostname or IP
- `user`: Database username
- `database`: Database name

### Optional Fields

- `port`: Database port (default: 5432 for postgres, 3306 for mysql)
- `password`: Database password (default: empty string)
- `sslmode`: PostgreSQL SSL mode (default: `prefer`)
- `ssh`: SSH tunnel configuration (object)
  - `host`: SSH server hostname/IP
  - `port`: SSH port (default: 22)
  - `user`: SSH username
  - `key`: Path to SSH private key

### Configuration Examples

**PostgreSQL with SSH tunnel:**

```bash
export DB_ALTA_DEV='{
  "type": "postgres",
  "host": "10.43.71.101",
  "port": 5432,
  "user": "postgres",
  "password": "secret",
  "database": "altadb",
  "sslmode": "disable",
  "ssh": {
    "host": "91.98.128.210",
    "port": 22,
    "user": "dbtunnel",
    "key": "~/.ssh/id_rsa"
  }
}'
```

**MySQL direct connection:**

```bash
export DB_MYAPP_PROD='{
  "type": "mysql",
  "host": "mysql.example.com",
  "port": 3306,
  "user": "produser",
  "password": "prodpass",
  "database": "production"
}'
```

**PostgreSQL minimal (local):**

```bash
export DB_LOCAL='{
  "type": "postgres",
  "host": "localhost",
  "user": "localuser",
  "database": "localdb"
}'
```

## SSH Tunnel Implementation

### Automatic Tunnel Management

The `DatabaseConnection` class in `db_api.py` implements automatic SSH tunnel lifecycle:

1. **Parse Configuration**: Load and validate DB\_\* environment variable
2. **Check SSH Config**: Determine if SSH tunnel is needed
3. **Create Tunnel**: Use `SSHTunnelForwarder` to create tunnel
4. **Get Local Port**: Retrieve dynamically assigned local port
5. **Connect Database**: Connect to 127.0.0.1:<local_port>
6. **Execute Operation**: Run query or schema inspection
7. **Cleanup**: Close database connection and stop tunnel

### Context Manager Pattern

```python
with db.connect() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT ...")
    results = cursor.fetchall()
```

Ensures:

- Automatic tunnel creation on enter
- Automatic cleanup on exit (success or error)
- No resource leaks
- Exception safety

### SSH Key Requirements

- Key-based authentication only
- Password authentication not supported
- Key must be readable by user running scripts
- Supports tilde (~) expansion in key paths
- Common locations: `~/.ssh/id_rsa`, `~/.ssh/id_ed25519`

### Tunnel Behavior

- **Ephemeral**: New tunnel for each operation
- **Random Port**: OS assigns local port dynamically
- **No State**: No persistent tunnel tracking
- **Clean Exit**: Always closed after operation
- **Error Handling**: Tunnel closed even on errors

## Database-Specific Notes

### PostgreSQL

**Supported Operations:**

- All standard SQL operations
- EXPLAIN/ANALYZE for query planning
- Schema inspection via information_schema
- Index inspection via pg_indexes

**SSL Modes:**

- `disable`: No SSL
- `prefer`: SSL if available (default)
- `require`: SSL required
- `verify-ca`: Verify certificate
- `verify-full`: Verify certificate and hostname

**Connection String Format:**

```python
psycopg2.connect(
    host='127.0.0.1',
    port=12345,
    user='postgres',
    password='secret',
    dbname='mydb',
    sslmode='disable'
)
```

### MySQL

**Supported Operations:**

- All standard SQL operations
- EXPLAIN for query planning
- Schema inspection via DESCRIBE and SHOW
- Index inspection via SHOW INDEXES

**Connection Parameters:**

```python
mysql.connector.connect(
    host='127.0.0.1',
    port=12345,
    user='myuser',
    password='secret',
    database='mydb'
)
```

**MySQL-Specific Notes:**

- No sslmode parameter (SSL handled differently)
- Uses `database` instead of `dbname`
- Different schema inspection queries

## Error Handling

### Configuration Errors

**Missing Environment Variable:**

```
Error: DB_INVALID_ENV environment variable not found
Hint: Source credentials from ~/.secrets file
```

**Invalid JSON:**

```
Error: Invalid JSON in DB_ALTA_DEV: Expecting property name enclosed in double quotes: line 2 column 3 (char 4)
```

**Missing Required Field:**

```
Error: Missing required field 'database' in DB_ALTA_DEV
```

### Connection Errors

**SSH Key Not Found:**

```
Error: SSH key not found at /Users/user/.ssh/missing_key
```

**SSH Connection Failed:**

```
Error: could not connect to SSH host: [Errno 61] Connection refused
```

**Database Connection Failed:**

```
Error: could not connect to server: Connection refused
```

**Authentication Failed:**

```
Error: FATAL: password authentication failed for user "postgres"
```

### Query Errors

**SQL Syntax Error:**

```json
{
  "status": "error",
  "error": "syntax error at or near \"FROM\"",
  "sql": "SELECT * FORM users"
}
```

**Table Not Found:**

```json
{
  "status": "error",
  "error": "relation \"missing_table\" does not exist",
  "sql": "SELECT * FROM missing_table"
}
```

## Debugging

### Enable Python Debugging

```bash
export PYTHONDONTWRITEBYTECODE=1

python3 -u connect.py ALTA_DEV 2>&1 | tee debug.log
```

### Test SSH Tunnel Manually

```bash
ssh -L 5432:10.43.71.101:5432 dbtunnel@91.98.128.210 -i ~/.ssh/id_rsa
```

### Test Database Connection Manually

**PostgreSQL:**

```bash
psql -h 127.0.0.1 -p 5432 -U postgres -d altadb
```

**MySQL:**

```bash
mysql -h 127.0.0.1 -P 3306 -u myuser -p mydb
```

### Check Environment Variables

```bash
source ~/.secrets

env | grep ^DB_
```

### Validate JSON Configuration

```bash
echo $DB_ALTA_DEV | jq .
```

## Performance Tips

1. **Combine Queries**: Execute multiple operations in one query when possible
2. **Use LIMIT**: Limit result sets for testing
3. **Index Usage**: Ensure proper indexes for queries
4. **Connection Overhead**: Each operation = new connection + tunnel setup (~1-2s)
5. **Large Results**: All results loaded into memory, use pagination

## Security Considerations

1. **Credentials**: Store in ~/.secrets, never commit to git
2. **SSH Keys**: Use read-only keys for production databases
3. **Database Users**: Use least-privilege database users
4. **SSL/TLS**: Enable SSL for production connections
5. **Tunnel Only**: Use SSH tunnels for remote databases
6. **No Passwords**: Avoid storing plaintext passwords

## Troubleshooting

### Package Import Errors

```bash
python3 -c "import sshtunnel"

pip3 install --user sshtunnel
```

### SSH Permission Denied

```bash
chmod 600 ~/.ssh/id_rsa

ssh-add ~/.ssh/id_rsa
```

### Database Connection Timeout

- Check firewall rules
- Verify SSH tunnel is working
- Check database is accepting connections
- Verify credentials

### JSON Parse Errors

- Use single quotes around JSON in bash: `'{"key":"value"}'`
- Escape special characters properly
- Validate JSON with `jq` before setting environment variable

## Development

### Adding New Database Types

1. Update `db_api.py` DatabaseConnection.\_create_connection()
2. Import appropriate database driver
3. Add connection parameters
4. Update schema.py for schema inspection queries
5. Update documentation

### Running Tests

```bash
source ~/.secrets

for env in $(python3 discover.py | jq -r '.[].env'); do
  echo "Testing $env..."
  python3 connect.py "$env" || echo "Failed: $env"
done
```

## Additional Resources

- **Main Documentation**: ../SKILL.md
- **Command Reference**: ../commands.md
- **Python sshtunnel**: https://github.com/pahaz/sshtunnel
- **psycopg2**: https://www.psycopg.org/docs/
- **MySQL Connector**: https://dev.mysql.com/doc/connector-python/en/
