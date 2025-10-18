#!/usr/bin/env python3

import sys
import json
from redmine_api import RedmineAPI


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-":
        time_entry_data = json.load(sys.stdin)
    else:
        print("Usage: log_time.py - (reads JSON from stdin)", file=sys.stderr)
        print("Example: echo '{\"issue_id\": 123, \"hours\": 2.5}' | log_time.py -", file=sys.stderr)
        sys.exit(1)

    api = RedmineAPI()

    payload = {"time_entry": time_entry_data}
    result = api.post("time_entries.json", payload)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
