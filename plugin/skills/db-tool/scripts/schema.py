#!/usr/bin/env python3

import sys
import json
import argparse
from db_api import DatabaseConfig, DatabaseConnection


def get_postgres_schema(cursor, table_name=None):
    if table_name:
        cursor.execute("""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))

        columns = []
        for row in cursor.fetchall():
            columns.append({
                'column_name': row[0],
                'data_type': row[1],
                'is_nullable': row[2],
                'column_default': row[3],
                'character_maximum_length': row[4]
            })

        cursor.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = %s
        """, (table_name,))

        indexes = []
        for row in cursor.fetchall():
            indexes.append({
                'index_name': row[0],
                'definition': row[1]
            })

        return {
            'table': table_name,
            'columns': columns,
            'indexes': indexes
        }
    else:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_name
        """)

        tables = [row[0] for row in cursor.fetchall()]
        return {'tables': tables}


def get_mysql_schema(cursor, table_name=None):
    if table_name:
        cursor.execute(f"DESCRIBE {table_name}")

        columns = []
        for row in cursor.fetchall():
            columns.append({
                'column_name': row[0],
                'data_type': row[1],
                'is_nullable': row[2],
                'key': row[3],
                'column_default': row[4],
                'extra': row[5]
            })

        cursor.execute(f"SHOW INDEXES FROM {table_name}")

        indexes = []
        for row in cursor.fetchall():
            indexes.append({
                'table': row[0],
                'non_unique': row[1],
                'key_name': row[2],
                'seq_in_index': row[3],
                'column_name': row[4]
            })

        return {
            'table': table_name,
            'columns': columns,
            'indexes': indexes
        }
    else:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        return {'tables': tables}


def main():
    parser = argparse.ArgumentParser(description="Inspect database schema")
    parser.add_argument("env", help="Environment name (e.g., ALTA_DEV)")
    parser.add_argument("table", nargs='?', help="Specific table name (optional)")

    args = parser.parse_args()

    try:
        config = DatabaseConfig(args.env)
        db = DatabaseConnection(config)

        with db.connect() as conn:
            cursor = conn.cursor()

            if config.db_type == 'postgres':
                result = get_postgres_schema(cursor, args.table)
            elif config.db_type == 'mysql':
                result = get_mysql_schema(cursor, args.table)
            else:
                print(f"Error: Unsupported database type '{config.db_type}'", file=sys.stderr)
                sys.exit(1)

            cursor.close()

            output = {
                'status': 'success',
                'env': args.env,
                'type': config.db_type,
                **result
            }

            print(json.dumps(output, indent=2))

    except Exception as e:
        output = {
            'status': 'error',
            'error': str(e)
        }
        print(json.dumps(output, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
