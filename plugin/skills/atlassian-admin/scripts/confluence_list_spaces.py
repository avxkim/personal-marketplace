#!/usr/bin/env python3

import sys
import json
import argparse
from confluence_api import ConfluenceAPI


def main():
    parser = argparse.ArgumentParser(description='List Confluence spaces')
    parser.add_argument('instance', help='Instance name (e.g., 4RA)')
    parser.add_argument('--limit', type=int, default=25, help='Max results (default: 25)')
    parser.add_argument('--start', type=int, default=0, help='Start at index (default: 0)')
    parser.add_argument('--type', help='Space type: global, personal')

    args = parser.parse_args()

    api = ConfluenceAPI(args.instance)

    params = {
        'limit': str(args.limit),
        'start': str(args.start)
    }

    if args.type:
        params['type'] = args.type

    result = api.get('space', params=params)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
