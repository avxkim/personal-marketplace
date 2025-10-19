#!/usr/bin/env python3

import sys
import json
import argparse
from db_api import DatabaseConfig, DatabaseConnection


def main():
    parser = argparse.ArgumentParser(description="Test database connection")
    parser.add_argument("env", help="Environment name (e.g., ALTA_DEV)")

    args = parser.parse_args()

    try:
        config = DatabaseConfig(args.env)
        db = DatabaseConnection(config)

        print(f"Testing connection to DB_{args.env}...", file=sys.stderr)

        if config.has_ssh_tunnel:
            print(f"Using SSH tunnel via {config.ssh_config['host']}...", file=sys.stderr)

        with db.connect() as conn:
            cursor = conn.cursor()

            if config.db_type == 'postgres':
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
            elif config.db_type == 'mysql':
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
            else:
                version = "Unknown"

            cursor.close()

            result = {
                'status': 'success',
                'env': args.env,
                'type': config.db_type,
                'host': config.host,
                'port': config.port,
                'database': config.database,
                'user': config.user,
                'ssh_tunnel': config.has_ssh_tunnel,
                'version': version
            }

            print(json.dumps(result, indent=2))

    except Exception as e:
        result = {
            'status': 'error',
            'env': args.env,
            'error': str(e)
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
