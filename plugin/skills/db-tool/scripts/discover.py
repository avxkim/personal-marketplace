#!/usr/bin/env python3

import os
import sys
import json
from typing import List, Dict, Any


def discover_databases() -> List[Dict[str, Any]]:
    databases = []

    for key, value in os.environ.items():
        if key.startswith('DB_') and key != 'DB_':
            env_name = key[3:]

            try:
                config = json.loads(value)

                db_info = {
                    'env': env_name,
                    'env_var': key,
                    'type': config.get('type', 'unknown'),
                    'host': config.get('host', 'unknown'),
                    'database': config.get('database', 'unknown'),
                    'user': config.get('user', 'unknown'),
                    'has_ssh_tunnel': 'ssh' in config and config['ssh'] is not None
                }

                databases.append(db_info)
            except json.JSONDecodeError:
                print(f"Warning: Skipping {key} - invalid JSON format", file=sys.stderr)
                continue

    databases.sort(key=lambda x: x['env'])

    return databases


def main():
    databases = discover_databases()

    if not databases:
        print("No database environments found", file=sys.stderr)
        print("Hint: Add DB_* environment variables to ~/.secrets", file=sys.stderr)
        print("Example: DB_MYAPP_DEV='{\"type\":\"postgres\",\"host\":\"...\",\"user\":\"...\",\"database\":\"...\"}'", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(databases, indent=2))


if __name__ == "__main__":
    main()
