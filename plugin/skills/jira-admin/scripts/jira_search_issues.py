#!/usr/bin/env python3

import sys
import json
import argparse
from jira_api import JiraAPI


def main():
    parser = argparse.ArgumentParser(description='Search Jira issues using JQL')
    parser.add_argument('instance', help='Instance name (e.g., 4RA)')
    parser.add_argument('jql', help='JQL query string')
    parser.add_argument('--max-results', type=int, default=50, help='Max results (default: 50)')
    parser.add_argument('--start-at', type=int, default=0, help='Start at index (default: 0)')
    parser.add_argument('--fields', help='Comma-separated fields to return')

    args = parser.parse_args()

    api = JiraAPI(args.instance)

    params = {
        'jql': args.jql,
        'maxResults': str(args.max_results),
        'startAt': str(args.start_at)
    }

    if args.fields:
        params['fields'] = args.fields

    result = api.get('search', params=params)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
