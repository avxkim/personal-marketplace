#!/usr/bin/env python3

import sys
import json
import argparse
from jira_api import JiraAPI


def main():
    parser = argparse.ArgumentParser(description='Get sprint details')
    parser.add_argument('instance', help='Instance name (e.g., 4RA)')
    parser.add_argument('sprint_id', help='Sprint ID')

    args = parser.parse_args()

    api = JiraAPI(args.instance)

    result = api.get(f'sprint/{args.sprint_id}')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
