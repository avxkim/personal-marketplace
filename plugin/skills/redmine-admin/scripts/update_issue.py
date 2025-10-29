#!/usr/bin/env python3

import sys
import json
from redmine_api import RedmineAPI

REDMINE_COMMENT_MAX_LENGTH = 2000


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

    if "notes" in update_data:
        notes_length = len(update_data["notes"])
        if notes_length > REDMINE_COMMENT_MAX_LENGTH:
            print(f"Error: Comment length ({notes_length} chars) exceeds Redmine limit ({REDMINE_COMMENT_MAX_LENGTH} chars)", file=sys.stderr)
            print(f"Hint: Comment is {notes_length - REDMINE_COMMENT_MAX_LENGTH} characters too long", file=sys.stderr)
            print("Hint: Consider splitting into multiple comments or shortening the text", file=sys.stderr)
            sys.exit(1)

    api = RedmineAPI()

    payload = {"issue": update_data}
    result = api.put(f"issues/{issue_id}.json", payload)

    print(json.dumps(result if result else {"success": True, "issue_id": issue_id}, indent=2))


if __name__ == "__main__":
    main()
