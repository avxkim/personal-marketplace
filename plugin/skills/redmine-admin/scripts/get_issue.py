#!/usr/bin/env python3

import sys
import json
from redmine_api import RedmineAPI


def main():
    if len(sys.argv) < 2:
        print("Usage: get_issue.py <ISSUE_ID>", file=sys.stderr)
        sys.exit(1)

    issue_id = sys.argv[1]

    api = RedmineAPI()
    result = api.get(f"issues/{issue_id}.json", params={"include": "attachments,journals,watchers"})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
