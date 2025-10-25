#!/usr/bin/env python3

import os
import json
import re

secrets_file = os.path.expanduser("~/.secrets")

instances = {}

if os.path.exists(secrets_file):
    with open(secrets_file, 'r') as f:
        for line in f:
            line = line.strip()

            if match := re.match(r'export\s+CONFLUENCE_([A-Z0-9_]+)_URL="?([^"]+)"?', line):
                instance_name = match.group(1)
                url = match.group(2)

                if instance_name not in instances:
                    instances[instance_name] = {}

                instances[instance_name]['url'] = url
                instances[instance_name]['name'] = instance_name

            elif match := re.match(r'export\s+CONFLUENCE_([A-Z0-9_]+)_(USERNAME|PASSWORD|PAT|BASIC_USER|BASIC_PASS)="?([^"]*)"?', line):
                instance_name = match.group(1)
                key = match.group(2).lower()
                value = match.group(3)

                if instance_name not in instances:
                    instances[instance_name] = {}

                instances[instance_name][key] = value

result = []
for name, config in instances.items():
    if 'url' not in config:
        continue

    has_nginx = bool(config.get('basic_user') and config.get('basic_pass'))
    has_pat = bool(config.get('pat'))
    has_password = bool(config.get('password'))

    if has_nginx:
        auth_type = "nginx-protected (browser authentication)"
    elif has_pat:
        auth_type = "PAT (direct API authentication)"
    elif has_password:
        auth_type = "password (basic authentication)"
    else:
        auth_type = "incomplete (missing credentials)"

    result.append({
        'name': name,
        'url': config['url'],
        'username': config.get('username', 'N/A'),
        'auth_type': auth_type,
        'has_nginx': has_nginx,
        'has_pat': has_pat,
        'has_password': has_password
    })

print(json.dumps(result, indent=2))
