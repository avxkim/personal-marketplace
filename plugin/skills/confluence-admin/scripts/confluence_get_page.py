#!/usr/bin/env python3

import sys
import json
from confluence_api import ConfluenceAPI

if len(sys.argv) < 3:
    print("Usage: confluence_get_page.py <instance> <page_id> [expand]", file=sys.stderr)
    print("  expand: body.storage,version,history,etc. (comma-separated)", file=sys.stderr)
    sys.exit(1)

instance = sys.argv[1]
page_id = sys.argv[2]
expand = sys.argv[3] if len(sys.argv) > 3 else "body.storage,version,space"

api = ConfluenceAPI(instance)

params = {}
if expand:
    params['expand'] = expand

result = api.get(f'content/{page_id}', params=params)

print(json.dumps(result, indent=2))
