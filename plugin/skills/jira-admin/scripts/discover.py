#!/usr/bin/env python3

import os
import sys
import json
import re


def discover_instances():
    instances = {}

    for key, value in os.environ.items():
        jira_match = re.match(r'JIRA_(.+)_TOKEN', key)

        if jira_match:
            instance = jira_match.group(1)
            if instance not in instances:
                instances[instance] = {}
            instances[instance]['jira'] = {
                'token_var': key,
                'url_var': f'JIRA_{instance}_URL',
                'url': os.getenv(f'JIRA_{instance}_URL'),
                'has_token': True
            }

    result = []
    for instance, services in instances.items():
        entry = {
            'instance': instance,
            'services': {}
        }

        if 'jira' in services:
            entry['services']['jira'] = {
                'url': services['jira']['url'],
                'configured': services['jira']['url'] is not None
            }

        result.append(entry)

    return result


if __name__ == '__main__':
    instances = discover_instances()
    print(json.dumps(instances, indent=2))
