#!/usr/bin/env python3

import sys
import json
import argparse
from confluence_api import ConfluenceAPI


def main():
    parser = argparse.ArgumentParser(description='Update Confluence page')
    parser.add_argument('instance', help='Instance name (e.g., 4RA)')
    parser.add_argument('page_id', help='Page ID')
    parser.add_argument('data', help='JSON data (use - for stdin)')

    args = parser.parse_args()

    api = ConfluenceAPI(args.instance)

    if args.data == '-':
        update_data = json.load(sys.stdin)
    else:
        update_data = json.loads(args.data)

    result = api.put(f'content/{args.page_id}', update_data)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
