#!/usr/bin/env python3

import sys
import json
import argparse
from datetime import datetime, timedelta
from redmine_api import RedmineAPI


def parse_month(month_str: str) -> tuple[str, str]:
    if month_str.lower() == "current":
        now = datetime.now()
        year = now.year
        month = now.month
    else:
        try:
            date_obj = datetime.strptime(month_str, "%Y-%m")
            year = date_obj.year
            month = date_obj.month
        except ValueError:
            print(f"Error: Invalid month format '{month_str}'. Use YYYY-MM or 'current'", file=sys.stderr)
            sys.exit(1)

    from_date = datetime(year, month, 1)

    if month == 12:
        to_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        to_date = datetime(year, month + 1, 1) - timedelta(days=1)

    return from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(description="Get Redmine time entries")
    parser.add_argument("--user-id", type=str, help="Filter by user ID ('me' or numeric ID)")
    parser.add_argument("--project-id", type=int, help="Filter by project ID")
    parser.add_argument("--issue-id", type=int, help="Filter by issue ID")
    parser.add_argument("--from", dest="from_date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--month", type=str, help="Month filter (YYYY-MM or 'current')")
    parser.add_argument("--limit", type=int, default=100, help="Max number of entries")

    args = parser.parse_args()

    api = RedmineAPI()

    params = {"limit": str(args.limit)}

    if args.month:
        from_date, to_date = parse_month(args.month)
        params["from"] = from_date
        params["to"] = to_date
    else:
        if args.from_date:
            params["from"] = args.from_date
        if args.to:
            params["to"] = args.to

    if args.user_id:
        params["user_id"] = args.user_id
    if args.project_id:
        params["project_id"] = str(args.project_id)
    if args.issue_id:
        params["issue_id"] = str(args.issue_id)

    result = api.get("time_entries.json", params=params)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
