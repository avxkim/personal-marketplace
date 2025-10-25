#!/usr/bin/env python3

import sys
import json
from confluence_api import ConfluenceAPI

if len(sys.argv) < 3:
    print("Usage: confluence_list_attachments.py <instance> <page_id> [limit]", file=sys.stderr)
    sys.exit(1)

instance = sys.argv[1]
page_id = sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50

api = ConfluenceAPI(instance)

params = {
    'limit': str(limit)
}

result = api.get(f'content/{page_id}/child/attachment', params=params)

print(json.dumps(result, indent=2))
