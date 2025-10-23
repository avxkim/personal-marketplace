#!/usr/bin/env python3

import sys
import json
import argparse
from jira_api import JiraAPI


def main():
    parser = argparse.ArgumentParser(description='Create Jira issue')
    parser.add_argument('instance', help='Instance name (e.g., 4RA)')
    parser.add_argument('data', help='JSON data (use - for stdin)')

    args = parser.parse_args()

    api = JiraAPI(args.instance)

    if args.data == '-':
        issue_data = json.load(sys.stdin)
    else:
        issue_data = json.loads(args.data)

    payload = {'fields': issue_data}
    result = api.post('issue', payload)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
