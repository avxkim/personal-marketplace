#!/usr/bin/env python3

import sys
import json
import argparse
from jira_api import JiraAPI


def main():
    parser = argparse.ArgumentParser(description='Update Jira issue')
    parser.add_argument('instance', help='Instance name (e.g., 4RA)')
    parser.add_argument('issue_key', help='Issue key (e.g., DEV-123)')
    parser.add_argument('data', help='JSON data (use - for stdin)')

    args = parser.parse_args()

    api = JiraAPI(args.instance)

    if args.data == '-':
        update_data = json.load(sys.stdin)
    else:
        update_data = json.loads(args.data)

    api.put(f'issue/{args.issue_key}', update_data)
    print(json.dumps({'status': 'success', 'message': f'Issue {args.issue_key} updated'}))


if __name__ == '__main__':
    main()
