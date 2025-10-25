#!/usr/bin/env python3

import sys
import json
from confluence_api import ConfluenceAPI

if len(sys.argv) < 3:
    print("Usage: confluence_get_space.py <instance> <space_key>", file=sys.stderr)
    sys.exit(1)

instance = sys.argv[1]
space_key = sys.argv[2]

api = ConfluenceAPI(instance)

result = api.get(f'space/{space_key}')

print(json.dumps(result, indent=2))
