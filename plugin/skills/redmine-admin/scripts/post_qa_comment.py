#!/usr/bin/env python3
import sys
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from redmine_api import RedmineAPI, REDMINE_COMMENT_MAX_LENGTH

def format_pass_comment(scope, environment, notes=None):
    comment = f"""# 🟢 QA PASS

**Scope:** {scope}
**Environment:** `{environment}`

## ✅ Result
No issues found - all tests passed successfully.
"""
    if notes:
        comment += f"\n## 📝 Additional Notes\n{notes}\n"
    return comment.strip()

def format_fail_comment(scope, environment, issues, notes=None):
    issue_count = len(issues)
    comment = f"""# 🔴 QA FAIL

**Scope:** {scope}
**Environment:** `{environment}`

## ⚠️ Issues Found ({issue_count})
"""
    for idx, issue in enumerate(issues, 1):
        comment += f"{idx}. {issue}\n"

    if notes:
        comment += f"\n## 📝 Additional Notes\n{notes}\n"
    return comment.strip()

def format_blocked_comment(scope, environment, blocker, notes=None):
    comment = f"""# 🟡 QA BLOCKED

**Scope:** {scope}
**Environment:** `{environment}`

## 🚫 Blocker
{blocker}
"""
    if notes:
        comment += f"\n## 📝 Additional Notes\n{notes}\n"
    return comment.strip()

def main():
    if len(sys.argv) < 2 or sys.argv[1] != "-":
        print("Error: This command requires JSON input from stdin", file=sys.stderr)
        print("Usage: echo '{...}' | post_qa_comment.py -", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    required_fields = ["issue_id", "status", "scope", "environment"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        print(f"Error: Missing required fields: {', '.join(missing)}", file=sys.stderr)
        print("Required: issue_id, status, scope, environment", file=sys.stderr)
        sys.exit(1)

    issue_id = data["issue_id"]
    status = data["status"].upper()
    scope = data["scope"]
    environment = data["environment"]
    notes = data.get("notes")
    private = data.get("private", False)

    valid_statuses = ["PASS", "FAIL", "BLOCKED"]
    if status not in valid_statuses:
        print(f"Error: Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}", file=sys.stderr)
        sys.exit(1)

    if status == "PASS":
        comment = format_pass_comment(scope, environment, notes)
    elif status == "FAIL":
        issues = data.get("issues", [])
        if not issues:
            print("Error: 'issues' array is required for FAIL status", file=sys.stderr)
            sys.exit(1)
        comment = format_fail_comment(scope, environment, issues, notes)
    elif status == "BLOCKED":
        blocker = data.get("blocker")
        if not blocker:
            print("Error: 'blocker' field is required for BLOCKED status", file=sys.stderr)
            sys.exit(1)
        comment = format_blocked_comment(scope, environment, blocker, notes)

    comment_length = len(comment)
    if comment_length > REDMINE_COMMENT_MAX_LENGTH:
        print(f"Error: Generated comment is {comment_length} characters, exceeds limit of {REDMINE_COMMENT_MAX_LENGTH}", file=sys.stderr)
        print("Suggestion: Shorten issue descriptions, scope, or notes", file=sys.stderr)
        sys.exit(1)

    api = RedmineAPI()

    update_payload = {
        "issue": {
            "notes": comment
        }
    }

    if private:
        update_payload["issue"]["private_notes"] = True

    result = api.put(f"issues/{issue_id}.json", update_payload)

    print(json.dumps({
        "success": True,
        "issue_id": issue_id,
        "comment_length": comment_length,
        "comment_preview": comment[:100] + "..." if len(comment) > 100 else comment
    }, indent=2))

if __name__ == "__main__":
    main()
