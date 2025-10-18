#!/usr/bin/env python3

import sys
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
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


def format_markdown_report(entries: list, from_date: str, to_date: str) -> str:
    user_hours = defaultdict(lambda: {"total": 0.0, "issues": defaultdict(float)})

    for entry in entries:
        user_name = entry.get("user", {}).get("name", "Unknown")
        hours = entry.get("hours", 0.0)
        issue_id = entry.get("issue", {}).get("id", "No Issue")

        user_hours[user_name]["total"] += hours
        user_hours[user_name]["issues"][issue_id] += hours

    report = f"# Time Report: {from_date} to {to_date}\n\n"

    for user, data in sorted(user_hours.items()):
        report += f"## {user}\n"
        report += f"**Total Hours:** {data['total']:.2f}h\n\n"

        if data["issues"]:
            report += "| Issue | Hours |\n"
            report += "|-------|-------|\n"
            for issue_id, hours in sorted(data["issues"].items(), key=lambda x: x[1], reverse=True):
                report += f"| #{issue_id} | {hours:.2f}h |\n"

        report += "\n"

    grand_total = sum(data["total"] for data in user_hours.values())
    report += f"**Grand Total:** {grand_total:.2f}h\n"

    return report


def main():
    parser = argparse.ArgumentParser(description="Generate time report from Redmine")
    parser.add_argument("--user-id", type=str, help="Filter by user ID")
    parser.add_argument("--project-id", type=int, help="Filter by project ID")
    parser.add_argument("--from", dest="from_date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--month", type=str, help="Month filter (YYYY-MM or 'current')")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format")

    args = parser.parse_args()

    api = RedmineAPI()

    params = {"limit": "1000"}

    if args.month:
        from_date, to_date = parse_month(args.month)
        params["from"] = from_date
        params["to"] = to_date
    else:
        from_date = args.from_date or datetime.now().strftime("%Y-%m-01")
        to_date = args.to or datetime.now().strftime("%Y-%m-%d")
        params["from"] = from_date
        params["to"] = to_date

    if args.user_id:
        params["user_id"] = args.user_id
    if args.project_id:
        params["project_id"] = str(args.project_id)

    result = api.get("time_entries.json", params=params)
    entries = result.get("time_entries", [])

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_markdown_report(entries, from_date, to_date))


if __name__ == "__main__":
    main()
