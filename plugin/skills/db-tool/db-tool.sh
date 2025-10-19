#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

source ~/.secrets 2>/dev/null || true

command="$1"
shift

case "$command" in
    discover)
        python3 "$SCRIPTS_DIR/discover.py" "$@"
        ;;
    connect)
        python3 "$SCRIPTS_DIR/connect.py" "$@"
        ;;
    query)
        python3 "$SCRIPTS_DIR/query.py" "$@"
        ;;
    schema)
        python3 "$SCRIPTS_DIR/schema.py" "$@"
        ;;
    --help|-h|help)
        echo "Database Tool - Manage database connections with SSH tunnel support"
        echo ""
        echo "Usage: db-tool.sh <command> [arguments]"
        echo ""
        echo "Available commands:"
        echo "  discover          - List all DB_* environments from ~/.secrets"
        echo "  connect <env>     - Test connection to database environment"
        echo "  query <env> <sql> - Execute SQL query (use '-' to read from stdin)"
        echo "  schema <env> [table] - Show database schema (tables or specific table)"
        echo "  --help, -h, help  - Show this help message"
        echo ""
        echo "Examples:"
        echo "  db-tool.sh discover"
        echo "  db-tool.sh connect ALTA_DEV"
        echo "  db-tool.sh query ALTA_DEV 'SELECT * FROM users LIMIT 10'"
        echo "  echo 'SELECT * FROM users' | db-tool.sh query ALTA_DEV -"
        echo "  db-tool.sh schema ALTA_DEV"
        echo "  db-tool.sh schema ALTA_DEV users"
        echo ""
        echo "Environment variable format (in ~/.secrets):"
        echo "  DB_<PROJECT>_<ENV>='{\"type\":\"postgres\",\"host\":\"...\",\"port\":5432,\"user\":\"...\",\"password\":\"...\",\"database\":\"...\",\"ssh\":{\"host\":\"...\",\"user\":\"...\",\"key\":\"~/.ssh/id_rsa\"}}'"
        exit 0
        ;;
    *)
        echo "Unknown command: $command" >&2
        echo "Available commands: discover, connect, query, schema" >&2
        echo "Use --help for more information" >&2
        exit 1
        ;;
esac
