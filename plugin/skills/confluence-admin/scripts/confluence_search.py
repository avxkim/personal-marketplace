#!/usr/bin/env python3

import sys
import json
from confluence_api import ConfluenceAPI

if len(sys.argv) < 3:
    print("Usage: confluence_search.py <instance> <cql_query> [limit]", file=sys.stderr)
    print("  cql_query: Confluence Query Language query", file=sys.stderr)
    print("  Example: 'type=page AND space=DEV AND title~\"api\"'", file=sys.stderr)
    sys.exit(1)

instance = sys.argv[1]
cql = sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 25

api = ConfluenceAPI(instance)

params = {
    'cql': cql,
    'limit': str(limit)
}

result = api.get('content/search', params=params)

print(json.dumps(result, indent=2))
