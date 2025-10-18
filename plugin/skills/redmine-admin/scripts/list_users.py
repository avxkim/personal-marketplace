#!/usr/bin/env python3

import sys
import json
import argparse
from redmine_api import RedmineAPI


def main():
    parser = argparse.ArgumentParser(description="List Redmine users")
    parser.add_argument("--status", type=str, choices=["1", "2", "3", "active", "registered", "locked"],
                        help="Filter by status (1/active, 2/registered, 3/locked)")
    parser.add_argument("--name", type=str, help="Filter by name (substring match)")
    parser.add_argument("--limit", type=int, default=100, help="Max number of users to return")
    parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")

    args = parser.parse_args()

    api = RedmineAPI()

    params = {
        "limit": str(args.limit),
        "offset": str(args.offset)
    }

    if args.status:
        status_map = {
            "active": "1",
            "registered": "2",
            "locked": "3"
        }
        params["status"] = status_map.get(args.status, args.status)

    if args.name:
        params["name"] = args.name

    result = api.get("users.json", params=params)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
