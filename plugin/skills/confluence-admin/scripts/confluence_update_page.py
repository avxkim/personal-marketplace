#!/usr/bin/env python3

import sys
import json
from confluence_api import ConfluenceAPI

if len(sys.argv) < 4:
    print("Usage: confluence_update_page.py <instance> <page_id> <json_file|->>", file=sys.stderr)
    print("  json_file: File containing update data or '-' for stdin", file=sys.stderr)
    print("""
Example JSON:
{
  "version": {"number": 2},
  "title": "Updated Page Title",
  "type": "page",
  "body": {
    "storage": {
      "value": "<p>Updated content</p>",
      "representation": "storage"
    }
  }
}
""", file=sys.stderr)
    sys.exit(1)

instance = sys.argv[1]
page_id = sys.argv[2]
json_file = sys.argv[3]

if json_file == '-':
    update_data = json.load(sys.stdin)
else:
    with open(json_file, 'r') as f:
        update_data = json.load(f)

api = ConfluenceAPI(instance)

result = api.put(f'content/{page_id}', data=update_data)

print(json.dumps(result, indent=2))
