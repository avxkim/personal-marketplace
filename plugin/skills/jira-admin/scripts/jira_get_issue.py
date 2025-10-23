#!/usr/bin/env python3

import sys
import json
import argparse
from jira_api import JiraAPI


def main():
    parser = argparse.ArgumentParser(description='Get Jira issue details')
    parser.add_argument('instance', help='Instance name (e.g., 4RA)')
    parser.add_argument('issue_key', help='Issue key (e.g., DEV-123)')
    parser.add_argument('--fields', help='Comma-separated fields to return')
    parser.add_argument('--expand', help='Comma-separated expand options (e.g., changelog,renderedFields)')

    args = parser.parse_args()

    api = JiraAPI(args.instance)

    params = {}
    if args.fields:
        params['fields'] = args.fields
    if args.expand:
        params['expand'] = args.expand

    result = api.get(f'issue/{args.issue_key}', params=params if params else None)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
