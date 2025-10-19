#!/usr/bin/env python3

import os
import sys
import json
from typing import Dict, Any, Optional, Tuple
from contextlib import contextmanager
from sshtunnel import SSHTunnelForwarder


class DatabaseConfig:
    def __init__(self, env_name: str):
        self.env_name = env_name
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        env_value = os.getenv(f"DB_{self.env_name}")

        if not env_value:
            print(f"Error: DB_{self.env_name} environment variable not found", file=sys.stderr)
            print(f"Hint: Source credentials from ~/.secrets file", file=sys.stderr)
            sys.exit(1)

        try:
            config = json.loads(env_value)
            required_fields = ['type', 'host', 'user', 'database']

            for field in required_fields:
                if field not in config:
                    print(f"Error: Missing required field '{field}' in DB_{self.env_name}", file=sys.stderr)
                    sys.exit(1)

            return config
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in DB_{self.env_name}: {e}", file=sys.stderr)
            sys.exit(1)

    @property
    def db_type(self) -> str:
        return self.config['type']

    @property
    def has_ssh_tunnel(self) -> bool:
        return 'ssh' in self.config and self.config['ssh']

    @property
    def host(self) -> str:
        return self.config['host']

    @property
    def port(self) -> int:
        return self.config.get('port', 5432 if self.db_type == 'postgres' else 3306)

    @property
    def user(self) -> str:
        return self.config['user']

    @property
    def password(self) -> str:
        return self.config.get('password', '')

    @property
    def database(self) -> str:
        return self.config['database']

    @property
    def sslmode(self) -> str:
        return self.config.get('sslmode', 'prefer')

    @property
    def ssh_config(self) -> Optional[Dict[str, Any]]:
        return self.config.get('ssh')


class DatabaseConnection:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.tunnel = None
        self.connection = None

    @contextmanager
    def connect(self):
        try:
            if self.config.has_ssh_tunnel:
                local_bind = self._setup_ssh_tunnel()
                host, port = local_bind
            else:
                host = self.config.host
                port = self.config.port

            self.connection = self._create_connection(host, port)
            yield self.connection

        finally:
            self._cleanup()

    def _setup_ssh_tunnel(self) -> Tuple[str, int]:
        ssh = self.config.ssh_config

        ssh_key = os.path.expanduser(ssh['key'])

        if not os.path.exists(ssh_key):
            print(f"Error: SSH key not found at {ssh_key}", file=sys.stderr)
            sys.exit(1)

        self.tunnel = SSHTunnelForwarder(
            (ssh['host'], ssh.get('port', 22)),
            ssh_username=ssh['user'],
            ssh_pkey=ssh_key,
            remote_bind_address=(self.config.host, self.config.port),
            allow_agent=False,
            host_pkey_directories=[]
        )

        self.tunnel.start()
        local_port = self.tunnel.local_bind_port

        return ('127.0.0.1', local_port)

    def _create_connection(self, host: str, port: int):
        if self.config.db_type == 'postgres':
            try:
                import psycopg2
            except ImportError:
                print("Error: psycopg2-binary not installed", file=sys.stderr)
                print("Install: pip3 install psycopg2-binary", file=sys.stderr)
                sys.exit(1)

            conn_params = {
                'host': host,
                'port': port,
                'user': self.config.user,
                'password': self.config.password,
                'dbname': self.config.database,
                'sslmode': self.config.sslmode
            }

            return psycopg2.connect(**conn_params)

        elif self.config.db_type == 'mysql':
            try:
                import mysql.connector
            except ImportError:
                print("Error: mysql-connector-python not installed", file=sys.stderr)
                print("Install: pip3 install mysql-connector-python", file=sys.stderr)
                sys.exit(1)

            conn_params = {
                'host': host,
                'port': port,
                'user': self.config.user,
                'password': self.config.password,
                'database': self.config.database
            }

            return mysql.connector.connect(**conn_params)

        else:
            print(f"Error: Unsupported database type '{self.config.db_type}'", file=sys.stderr)
            print(f"Supported types: postgres, mysql", file=sys.stderr)
            sys.exit(1)

    def _cleanup(self):
        if self.connection:
            try:
                self.connection.close()
            except:
                pass

        if self.tunnel:
            try:
                self.tunnel.stop()
            except:
                pass


def execute_query(env_name: str, query: str, fetch: bool = True) -> Any:
    config = DatabaseConfig(env_name)
    db = DatabaseConnection(config)

    with db.connect() as conn:
        cursor = conn.cursor()

        try:
            cursor.execute(query)

            if fetch and cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return {'columns': columns, 'rows': rows}
            else:
                conn.commit()
                return {'affected_rows': cursor.rowcount}

        finally:
            cursor.close()
