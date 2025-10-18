#!/usr/bin/env python3

import sys
import json
from redmine_api import RedmineAPI


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-":
        issue_data = json.load(sys.stdin)
    else:
        print("Usage: create_issue.py - (reads JSON from stdin)", file=sys.stderr)
        print("Example: echo '{\"project_id\": 1, \"subject\": \"Title\"}' | create_issue.py -", file=sys.stderr)
        sys.exit(1)

    api = RedmineAPI()

    payload = {"issue": issue_data}
    result = api.post("issues.json", payload)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
