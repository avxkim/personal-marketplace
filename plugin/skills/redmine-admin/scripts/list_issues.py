#!/usr/bin/env python3

import sys
import json
import argparse
from redmine_api import RedmineAPI


def main():
    parser = argparse.ArgumentParser(description="List Redmine issues")
    parser.add_argument("--project-id", type=int, help="Filter by project ID")
    parser.add_argument("--status-id", type=str, help="Filter by status ID (or 'open', 'closed', '*')")
    parser.add_argument("--assigned-to", type=str, help="Filter by assigned user ('me' or user ID)")
    parser.add_argument("--tracker-id", type=int, help="Filter by tracker ID")
    parser.add_argument("--limit", type=int, default=100, help="Max number of issues to return")
    parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")

    args = parser.parse_args()

    api = RedmineAPI()

    params = {
        "limit": str(args.limit),
        "offset": str(args.offset)
    }

    if args.project_id:
        params["project_id"] = str(args.project_id)
    if args.status_id:
        params["status_id"] = args.status_id
    if args.assigned_to:
        params["assigned_to_id"] = args.assigned_to
    if args.tracker_id:
        params["tracker_id"] = str(args.tracker_id)

    result = api.get("issues.json", params=params)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
