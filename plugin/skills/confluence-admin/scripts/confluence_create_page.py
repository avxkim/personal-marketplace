#!/usr/bin/env python3

import sys
import json
from confluence_api import ConfluenceAPI

if len(sys.argv) < 3:
    print("Usage: confluence_create_page.py <instance> <json_file|->>", file=sys.stderr)
    print("  json_file: File containing page data or '-' for stdin", file=sys.stderr)
    print("""
Example JSON:
{
  "type": "page",
  "title": "My New Page",
  "space": {"key": "DEV"},
  "body": {
    "storage": {
      "value": "<p>Page content in storage format</p>",
      "representation": "storage"
    }
  }
}
""", file=sys.stderr)
    sys.exit(1)

instance = sys.argv[1]
json_file = sys.argv[2]

if json_file == '-':
    page_data = json.load(sys.stdin)
else:
    with open(json_file, 'r') as f:
        page_data = json.load(f)

api = ConfluenceAPI(instance)

result = api.post('content', data=page_data)

print(json.dumps(result, indent=2))
