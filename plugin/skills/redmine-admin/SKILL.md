---
name: Redmine Admin
description: Manage Redmine via REST API. ALWAYS use when user mentions Redmine URLs, issues, tasks, wiki pages, time entries, or projects. Handles reading wiki pages, managing issues, logging time, and generating reports.
allowed-tools: Bash, Read, Grep, WebFetch, BashOutput, KillShell
---

# Redmine Admin

This skill provides utilities for managing Redmine project management system via REST API.

## Core Capabilities

1. **Wiki Pages**: Read wiki page content from URLs or project/page names
2. **Issue Management**: List, create, update, and read issues
3. **Time Entry Management**: Log time, retrieve time entries by user/date
4. **Project Management**: List projects and their details
5. **User Management**: Retrieve user information
6. **Reporting**: Generate time reports for developers

## When to Use This Skill

**IMPORTANT**: Invoke this skill whenever the user mentions:

- **Any Redmine URL** (including wiki pages, issues, projects)
- Redmine issues, tasks, or tickets
- Time logging or time entries in Redmine
- Redmine reports or project information

Specific use cases:

- Read Redmine wiki pages (extracts content from wiki URLs)
- List or search Redmine issues/tasks
- Create new issues with specific fields
- Update issue status, assignee, or other fields
- Log time entries for tasks
- Generate time reports for developers (daily, weekly, monthly)
- Retrieve project information
- Query user assignments and workload

## Prerequisites

**Required Environment Variables:**

- `REDMINE_API_KEY` - Your Redmine API key
- `REDMINE_URL` - Redmine instance URL

**Required Tools:**

- Python 3
- `jq` (for JSON processing)

## Finding the Plugin Location

**IMPORTANT**: Before using this skill's scripts, locate the redmine-tool wrapper.

**Method 1: Auto-discover (works with any marketplace name)**

```bash
REDMINE_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/redmine-admin/redmine-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)
```

**Method 2: Direct lookup (faster, requires knowing marketplace name)**

```bash
REDMINE_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/redmine-admin/redmine-tool.sh
```

All commands below use `$REDMINE_TOOL` as the entry point.

## Quick Command Reference

All commands are invoked via the `redmine-tool.sh` wrapper script.

### 1. List Issues

```bash
# List all issues for a project
"$REDMINE_TOOL" list-issues --project-id 1

# List issues with filters
"$REDMINE_TOOL" list-issues --project-id 1 --status-id 1 --assigned-to me

# List issues with custom query
"$REDMINE_TOOL" list-issues --project-id 1 --limit 50
```

Returns JSON array of issues with id, subject, status, assignee, etc.

### 2. Get Issue Details

```bash
"$REDMINE_TOOL" get-issue 564
```

Returns full JSON object with all issue fields including custom fields.

### 3. Create Issue

```bash
cat <<'EOF' | "$REDMINE_TOOL" create-issue -
{
  "project_id": 1,
  "subject": "Issue title",
  "description": "Issue description",
  "priority_id": 2,
  "assigned_to_id": 5
}
EOF
```

Returns created issue JSON with new issue ID.

### 4. Update Issue

```bash
cat <<'EOF' | "$REDMINE_TOOL" update-issue 564 -
{
  "status_id": 2,
  "notes": "Moving to in progress"
}
EOF
```

Returns updated issue JSON.

### 5. Log Time Entry

```bash
cat <<'EOF' | "$REDMINE_TOOL" log-time -
{
  "issue_id": 564,
  "hours": 2.5,
  "activity_id": 9,
  "comments": "Working on feature implementation",
  "spent_on": "2025-10-19"
}
EOF
```

Returns created time entry JSON.

### 6. Get Time Entries

```bash
# Get time entries for a specific user in date range
"$REDMINE_TOOL" get-time-entries --user-id 5 --from 2025-10-01 --to 2025-10-31

# Get time entries for current month
"$REDMINE_TOOL" get-time-entries --user-id 5 --month current

# Get all time entries for a project
"$REDMINE_TOOL" get-time-entries --project-id 1
```

Returns JSON array of time entries.

### 7. Generate Time Report

```bash
# Monthly report for all users
"$REDMINE_TOOL" time-report --month 2025-10

# Monthly report for specific user
"$REDMINE_TOOL" time-report --user-id 5 --month 2025-10

# Custom date range
"$REDMINE_TOOL" time-report --from 2025-10-01 --to 2025-10-15
```

Returns formatted report with total hours per user/issue.

### 8. List Projects

```bash
"$REDMINE_TOOL" list-projects
```

Returns JSON array of all accessible projects.

### 9. Get Current User

```bash
"$REDMINE_TOOL" get-current-user
```

Returns JSON with current authenticated user details.

### 10. List Users

```bash
# List all users
"$REDMINE_TOOL" list-users

# List only active users
"$REDMINE_TOOL" list-users --status active

# List locked/inactive users
"$REDMINE_TOOL" list-users --status locked

# Search users by name
"$REDMINE_TOOL" list-users --name "Kim"
```

Returns JSON array of users with optional status filtering (active/registered/locked).

### 11. Get Wiki Page

```bash
# Get wiki page by URL
"$REDMINE_TOOL" get-wiki --url "https://redmine.int-tro.kz/projects/alta/wiki/Release-003"

# Get wiki page by project and page name
"$REDMINE_TOOL" get-wiki --project-id alta --page Release-003

# Get wiki page in JSON format
"$REDMINE_TOOL" get-wiki --url "https://redmine.int-tro.kz/projects/alta/wiki/Release-003" --format json
```

Returns wiki page content with metadata (text format by default, JSON optional).

## Complete Workflow Examples

### Create Issue and Log Time

```bash
# Locate tool
REDMINE_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/redmine-admin/redmine-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

# Create issue
ISSUE_JSON=$(cat <<'EOF' | "$REDMINE_TOOL" create-issue -
{
  "project_id": 1,
  "subject": "Fix authentication bug",
  "description": "Users unable to login with email",
  "priority_id": 3,
  "tracker_id": 1
}
EOF
)

ISSUE_ID=$(echo "$ISSUE_JSON" | jq -r '.issue.id')

# Log time on the issue
cat <<EOF | "$REDMINE_TOOL" log-time -
{
  "issue_id": $ISSUE_ID,
  "hours": 3.0,
  "activity_id": 9,
  "comments": "Fixed OAuth integration",
  "spent_on": "$(date +%Y-%m-%d)"
}
EOF
```

### Generate Monthly Time Report

```bash
# Get time entries for October 2025
ENTRIES=$("$REDMINE_TOOL" get-time-entries --month 2025-10)

# Generate formatted report
"$REDMINE_TOOL" time-report --month 2025-10 --format markdown
```

## Additional Documentation

- **[commands.md](commands.md)** - Detailed command reference with full API parameters and examples

## Integration Notes

- All API requests include proper authentication via `X-Redmine-API-Key` header
- API key is read from `$REDMINE_API_KEY` environment variable
- Base URL defaults to https://redmine.int-tro.kz but can be overridden with `$REDMINE_URL`
- All scripts return valid JSON for easy parsing with `jq`
- Error messages are sent to stderr, valid output to stdout

## Key Points

✅ **Always set REDMINE_API_KEY** - Required for authentication
✅ **Use heredoc for JSON input** - Avoid escaping errors (create-issue, update-issue, log-time)
✅ **Date format: YYYY-MM-DD** - ISO 8601 format for all date parameters
✅ **Check API response** - All commands return JSON with potential error fields

---

**For detailed command documentation, see [commands.md](commands.md)**
