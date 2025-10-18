#!/usr/bin/env python3

import sys
import json
from redmine_api import RedmineAPI


def main():
    if len(sys.argv) < 3:
        print("Usage: update_issue.py <ISSUE_ID> - (reads JSON from stdin)", file=sys.stderr)
        print("Example: echo '{\"status_id\": 2}' | update_issue.py 123 -", file=sys.stderr)
        sys.exit(1)

    issue_id = sys.argv[1]

    if sys.argv[2] == "-":
        update_data = json.load(sys.stdin)
    else:
        print("Error: Use '-' to read from stdin", file=sys.stderr)
        sys.exit(1)

    api = RedmineAPI()

    payload = {"issue": update_data}
    result = api.put(f"issues/{issue_id}.json", payload)

    print(json.dumps(result if result else {"success": True, "issue_id": issue_id}, indent=2))


if __name__ == "__main__":
    main()
