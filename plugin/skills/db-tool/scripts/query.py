#!/usr/bin/env python3

import sys
import json
import argparse
from db_api import DatabaseConfig, DatabaseConnection


def main():
    parser = argparse.ArgumentParser(description="Execute SQL query")
    parser.add_argument("env", help="Environment name (e.g., ALTA_DEV)")
    parser.add_argument("sql", nargs='?', help="SQL query to execute (or use stdin with -)")

    args = parser.parse_args()

    if args.sql == '-' or args.sql is None:
        sql = sys.stdin.read().strip()
    else:
        sql = args.sql

    if not sql:
        print("Error: No SQL query provided", file=sys.stderr)
        sys.exit(1)

    try:
        config = DatabaseConfig(args.env)
        db = DatabaseConnection(config)

        with db.connect() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(sql)

                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()

                    results = []
                    for row in rows:
                        row_dict = {}
                        for i, col in enumerate(columns):
                            value = row[i]
                            if value is not None:
                                row_dict[col] = str(value) if not isinstance(value, (int, float, bool)) else value
                            else:
                                row_dict[col] = None
                        results.append(row_dict)

                    output = {
                        'status': 'success',
                        'columns': columns,
                        'rows': results,
                        'row_count': len(results)
                    }
                else:
                    conn.commit()
                    output = {
                        'status': 'success',
                        'affected_rows': cursor.rowcount
                    }

                print(json.dumps(output, indent=2))

            finally:
                cursor.close()

    except Exception as e:
        output = {
            'status': 'error',
            'error': str(e),
            'sql': sql
        }
        print(json.dumps(output, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
