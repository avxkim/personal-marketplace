#!/usr/bin/env python3

import sys
import json
from confluence_api import ConfluenceAPI

if len(sys.argv) < 2:
    print("Usage: confluence_list_spaces.py <instance> [limit] [type]", file=sys.stderr)
    print("  type: global, personal, or all (default: all)", file=sys.stderr)
    sys.exit(1)

instance = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 25
space_type = sys.argv[3] if len(sys.argv) > 3 else "all"

api = ConfluenceAPI(instance)

params = {
    'limit': str(limit)
}

if space_type != "all":
    params['type'] = space_type

result = api.get('space', params=params)

print(json.dumps(result, indent=2))
