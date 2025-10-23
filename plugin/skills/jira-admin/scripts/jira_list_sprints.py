#!/usr/bin/env python3

import sys
import json
import argparse
from jira_api import JiraAPI


def main():
    parser = argparse.ArgumentParser(description='List sprints for a board')
    parser.add_argument('instance', help='Instance name (e.g., 4RA)')
    parser.add_argument('board_id', help='Board ID')
    parser.add_argument('--state', help='Sprint state: future, active, closed')
    parser.add_argument('--max-results', type=int, default=50, help='Max results (default: 50)')

    args = parser.parse_args()

    api = JiraAPI(args.instance)

    params = {
        'maxResults': str(args.max_results)
    }

    if args.state:
        params['state'] = args.state

    endpoint = f'board/{args.board_id}/sprint'
    result = api.get(endpoint, params=params)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
