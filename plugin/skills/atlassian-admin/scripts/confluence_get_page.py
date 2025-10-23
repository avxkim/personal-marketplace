#!/usr/bin/env python3

import sys
import json
import argparse
import re
import urllib.parse
from confluence_api import ConfluenceAPI


def extract_page_id_from_url(url):
    match = re.search(r'/pages/(\d+)/', url)
    if match:
        return match.group(1)

    match = re.search(r'pageId=(\d+)', url)
    if match:
        return match.group(1)

    return None


def main():
    parser = argparse.ArgumentParser(description='Get Confluence page')
    parser.add_argument('instance', help='Instance name (e.g., 4RA)')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='Page URL')
    group.add_argument('--page-id', help='Page ID')
    parser.add_argument('--space', help='Space key (use with --title)')
    parser.add_argument('--title', help='Page title (use with --space)')
    parser.add_argument('--expand', default='body.storage,version', help='Expand options')

    args = parser.parse_args()

    api = ConfluenceAPI(args.instance)

    if args.url:
        page_id = extract_page_id_from_url(args.url)
        if not page_id:
            print(f"Error: Could not extract page ID from URL", file=sys.stderr)
            sys.exit(1)
        result = api.get(f'content/{page_id}', params={'expand': args.expand})
    elif args.page_id:
        result = api.get(f'content/{args.page_id}', params={'expand': args.expand})
    elif args.space and args.title:
        params = {
            'spaceKey': args.space,
            'title': args.title,
            'expand': args.expand
        }
        result = api.get('content', params=params)
        if result.get('results'):
            result = result['results'][0]
        else:
            print(f"Error: Page not found", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Must provide --url, --page-id, or both --space and --title", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
