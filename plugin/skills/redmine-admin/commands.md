# Redmine Admin - Command Reference

Detailed documentation for all redmine-tool commands.

## Prerequisites

Required environment variables:

- `REDMINE_API_KEY` - Your Redmine API key
- `REDMINE_URL` - Redmine instance URL

---

## Command: list-issues

**Purpose**: Retrieve a list of issues based on various filters.

**Usage**:

```bash
"$REDMINE_TOOL" list-issues [OPTIONS]
```

**Options**:

- `--project-id <ID>`: Filter by project ID (e.g., 1)
- `--status-id <STATUS>`: Filter by status ('open', 'closed', '\*', or numeric ID)
- `--assigned-to <USER>`: Filter by assignee ('me' or numeric user ID)
- `--tracker-id <ID>`: Filter by tracker type ID
- `--limit <N>`: Maximum number of issues to return (default: 100)
- `--offset <N>`: Pagination offset (default: 0)

**Output** (JSON):

```json
{
  "issues": [
    {
      "id": 564,
      "project": { "id": 1, "name": "Alta" },
      "tracker": { "id": 1, "name": "Bug" },
      "status": { "id": 1, "name": "New" },
      "priority": { "id": 2, "name": "Normal" },
      "author": { "id": 1, "name": "Admin" },
      "subject": "Issue title",
      "description": "Issue description",
      "created_on": "2025-10-01T10:00:00Z",
      "updated_on": "2025-10-01T10:00:00Z"
    }
  ],
  "total_count": 150,
  "offset": 0,
  "limit": 100
}
```

**Examples**:

```bash
# List all open issues in project 1
"$REDMINE_TOOL" list-issues --project-id 1 --status-id open

# List issues assigned to me
"$REDMINE_TOOL" list-issues --assigned-to me

# List first 50 issues
"$REDMINE_TOOL" list-issues --limit 50

# Pagination - get next 100 issues
"$REDMINE_TOOL" list-issues --limit 100 --offset 100
```

**Exit Codes**:

- 0: Success
- 1: Error (API error, authentication failure, or network error)

---

## Command: get-issue

**Purpose**: Retrieve detailed information about a specific issue.

**Usage**:

```bash
"$REDMINE_TOOL" get-issue <ISSUE_ID>
```

**Parameters**:

- `ISSUE_ID`: Numeric issue ID (e.g., 564)

**Output** (JSON):

```json
{
  "issue": {
    "id": 564,
    "project": { "id": 1, "name": "Alta" },
    "tracker": { "id": 1, "name": "Bug" },
    "status": { "id": 1, "name": "New" },
    "priority": { "id": 2, "name": "Normal" },
    "author": { "id": 1, "name": "Admin" },
    "assigned_to": { "id": 5, "name": "Developer" },
    "subject": "Issue title",
    "description": "Detailed description",
    "start_date": "2025-10-01",
    "due_date": "2025-10-15",
    "done_ratio": 0,
    "estimated_hours": 8.0,
    "created_on": "2025-10-01T10:00:00Z",
    "updated_on": "2025-10-01T10:00:00Z",
    "attachments": [],
    "journals": [],
    "watchers": []
  }
}
```

**Examples**:

```bash
# Get issue #564
"$REDMINE_TOOL" get-issue 564

# Parse specific fields with jq
"$REDMINE_TOOL" get-issue 564 | jq -r '.issue.subject'
"$REDMINE_TOOL" get-issue 564 | jq -r '.issue.status.name'
```

**Exit Codes**:

- 0: Success
- 1: Error (issue not found, API error, or authentication failure)

---

## Command: create-issue

**Purpose**: Create a new issue in Redmine.

**Usage**:

```bash
cat <<'EOF' | "$REDMINE_TOOL" create-issue -
{
  "project_id": 1,
  "subject": "Issue title",
  "description": "Issue description"
}
EOF
```

**Required Fields**:

- `project_id`: Numeric project ID (required)
- `subject`: Issue title (required)

**Optional Fields**:

- `description`: Issue description
- `tracker_id`: Tracker type ID (default: project's default tracker)
- `status_id`: Status ID (default: 1 - New)
- `priority_id`: Priority ID (default: 2 - Normal)
- `assigned_to_id`: User ID to assign
- `start_date`: Start date (YYYY-MM-DD)
- `due_date`: Due date (YYYY-MM-DD)
- `estimated_hours`: Estimated hours (numeric)
- `done_ratio`: Completion percentage (0-100)
- `parent_issue_id`: Parent issue ID for subtasks
- `custom_fields`: Array of custom field values

**Output** (JSON):

```json
{
  "issue": {
    "id": 565,
    "project": {"id": 1, "name": "Alta"},
    "subject": "Issue title",
    ...
  }
}
```

**Examples**:

```bash
# Basic issue
cat <<'EOF' | "$REDMINE_TOOL" create-issue -
{
  "project_id": 1,
  "subject": "Fix login bug",
  "description": "Users cannot login with email"
}
EOF

# Issue with full details
cat <<'EOF' | "$REDMINE_TOOL" create-issue -
{
  "project_id": 1,
  "tracker_id": 1,
  "subject": "Implement user authentication",
  "description": "Add OAuth2 authentication",
  "priority_id": 3,
  "assigned_to_id": 5,
  "start_date": "2025-10-20",
  "due_date": "2025-10-27",
  "estimated_hours": 16.0
}
EOF

# Capture new issue ID
ISSUE_JSON=$(cat <<'EOF' | "$REDMINE_TOOL" create-issue -
{"project_id": 1, "subject": "New task"}
EOF
)
ISSUE_ID=$(echo "$ISSUE_JSON" | jq -r '.issue.id')
echo "Created issue #$ISSUE_ID"
```

**Exit Codes**:

- 0: Success
- 1: Error (validation error, permission denied, or API error)

---

## Command: update-issue

**Purpose**: Update an existing issue.

**Usage**:

```bash
cat <<'EOF' | "$REDMINE_TOOL" update-issue <ISSUE_ID> -
{
  "status_id": 2,
  "notes": "Update comment"
}
EOF
```

**Parameters**:

- `ISSUE_ID`: Numeric issue ID to update

**Updatable Fields**:

- `subject`: Change issue title
- `description`: Change description
- `status_id`: Change status
- `priority_id`: Change priority
- `assigned_to_id`: Reassign issue
- `done_ratio`: Update completion percentage
- `estimated_hours`: Update estimate
- `start_date`: Update start date
- `due_date`: Update due date
- `notes`: Add comment/note to issue
- `private_notes`: Set to true for private note

**Output** (JSON):

```json
{
  "success": true,
  "issue_id": "564"
}
```

**Examples**:

```bash
# Change status to "In Progress" with comment
cat <<'EOF' | "$REDMINE_TOOL" update-issue 564 -
{
  "status_id": 2,
  "notes": "Started working on this issue"
}
EOF

# Reassign and update progress
cat <<'EOF' | "$REDMINE_TOOL" update-issue 564 -
{
  "assigned_to_id": 7,
  "done_ratio": 50,
  "notes": "Reassigning to QA for testing"
}
EOF

# Close issue
cat <<'EOF' | "$REDMINE_TOOL" update-issue 564 -
{
  "status_id": 5,
  "done_ratio": 100,
  "notes": "Fixed and deployed"
}
EOF
```

**Exit Codes**:

- 0: Success
- 1: Error (issue not found, permission denied, or validation error)

---

## Command: log-time

**Purpose**: Log time entry for an issue.

**Usage**:

```bash
cat <<'EOF' | "$REDMINE_TOOL" log-time -
{
  "issue_id": 564,
  "hours": 2.5,
  "comments": "Work description"
}
EOF
```

**Required Fields**:

- `hours`: Time spent (numeric, can be decimal like 2.5)

**Optional Fields**:

- `issue_id`: Issue ID to log time against
- `project_id`: Project ID (if not logging against specific issue)
- `spent_on`: Date (YYYY-MM-DD, defaults to today)
- `activity_id`: Activity type ID (default: 9 - Development)
- `comments`: Description of work done

**Common Activity IDs**:

- 8: Design
- 9: Development
- 10: Testing
- 11: Deployment
- 12: Documentation

**Output** (JSON):

```json
{
  "time_entry": {
    "id": 1234,
    "project": { "id": 1, "name": "Alta" },
    "issue": { "id": 564 },
    "user": { "id": 1, "name": "Admin" },
    "activity": { "id": 9, "name": "Development" },
    "hours": 2.5,
    "comments": "Work description",
    "spent_on": "2025-10-19",
    "created_on": "2025-10-19T15:30:00Z",
    "updated_on": "2025-10-19T15:30:00Z"
  }
}
```

**Examples**:

```bash
# Log time for today
cat <<'EOF' | "$REDMINE_TOOL" log-time -
{
  "issue_id": 564,
  "hours": 3.0,
  "activity_id": 9,
  "comments": "Implemented user authentication"
}
EOF

# Log time for specific date
cat <<'EOF' | "$REDMINE_TOOL" log-time -
{
  "issue_id": 564,
  "hours": 4.5,
  "activity_id": 9,
  "comments": "Fixed bugs in OAuth flow",
  "spent_on": "2025-10-18"
}
EOF

# Log time to project without specific issue
cat <<'EOF' | "$REDMINE_TOOL" log-time -
{
  "project_id": 1,
  "hours": 1.0,
  "activity_id": 12,
  "comments": "Updated project documentation"
}
EOF
```

**Exit Codes**:

- 0: Success
- 1: Error (permission denied, invalid hours, or API error)

---

## Command: get-time-entries

**Purpose**: Retrieve time entries with various filters.

**Usage**:

```bash
"$REDMINE_TOOL" get-time-entries [OPTIONS]
```

**Options**:

- `--user-id <ID>`: Filter by user ID (or 'me')
- `--project-id <ID>`: Filter by project ID
- `--issue-id <ID>`: Filter by issue ID
- `--from <DATE>`: Start date (YYYY-MM-DD)
- `--to <DATE>`: End date (YYYY-MM-DD)
- `--month <MONTH>`: Month filter (YYYY-MM or 'current')
- `--limit <N>`: Max entries to return (default: 100)

**Output** (JSON):

```json
{
  "time_entries": [
    {
      "id": 1234,
      "project": { "id": 1, "name": "Alta" },
      "issue": { "id": 564 },
      "user": { "id": 1, "name": "Admin" },
      "activity": { "id": 9, "name": "Development" },
      "hours": 2.5,
      "comments": "Work description",
      "spent_on": "2025-10-19",
      "created_on": "2025-10-19T15:30:00Z"
    }
  ],
  "total_count": 45,
  "offset": 0,
  "limit": 100
}
```

**Examples**:

```bash
# Get all time entries for current month
"$REDMINE_TOOL" get-time-entries --month current

# Get time entries for specific user in October 2025
"$REDMINE_TOOL" get-time-entries --user-id 5 --month 2025-10

# Get my time entries for date range
"$REDMINE_TOOL" get-time-entries --user-id me --from 2025-10-01 --to 2025-10-15

# Get all time entries for specific issue
"$REDMINE_TOOL" get-time-entries --issue-id 564

# Get time entries for project
"$REDMINE_TOOL" get-time-entries --project-id 1 --limit 200
```

**Exit Codes**:

- 0: Success
- 1: Error (invalid date format, API error, or authentication failure)

---

## Command: time-report

**Purpose**: Generate formatted time reports with aggregation by user and issue.

**Usage**:

```bash
"$REDMINE_TOOL" time-report [OPTIONS]
```

**Options**:

- `--user-id <ID>`: Filter by user ID
- `--project-id <ID>`: Filter by project ID
- `--from <DATE>`: Start date (YYYY-MM-DD)
- `--to <DATE>`: End date (YYYY-MM-DD)
- `--month <MONTH>`: Month filter (YYYY-MM or 'current')
- `--format <FORMAT>`: Output format ('json' or 'markdown', default: markdown)

**Output** (Markdown):

```markdown
# Time Report: 2025-10-01 to 2025-10-31

## Alexander Kim

**Total Hours:** 85.50h

| Issue | Hours  |
| ----- | ------ |
| #564  | 32.00h |
| #563  | 28.50h |
| #562  | 15.00h |
| #561  | 10.00h |

## Developer Name

**Total Hours:** 62.00h

| Issue | Hours  |
| ----- | ------ |
| #565  | 40.00h |
| #566  | 22.00h |

**Grand Total:** 147.50h
```

**Output** (JSON):

```json
{
  "time_entries": [...],
  "total_count": 250
}
```

**Examples**:

```bash
# Current month report for all users
"$REDMINE_TOOL" time-report --month current

# October 2025 report
"$REDMINE_TOOL" time-report --month 2025-10

# Report for specific user
"$REDMINE_TOOL" time-report --user-id 5 --month 2025-10

# Custom date range report
"$REDMINE_TOOL" time-report --from 2025-10-01 --to 2025-10-15

# JSON format for further processing
"$REDMINE_TOOL" time-report --month current --format json | jq '.time_entries[] | select(.user.id == 5)'
```

**Exit Codes**:

- 0: Success
- 1: Error (invalid date, API error, or authentication failure)

---

## Command: list-projects

**Purpose**: Retrieve list of all accessible projects.

**Usage**:

```bash
"$REDMINE_TOOL" list-projects
```

**Output** (JSON):

```json
{
  "projects": [
    {
      "id": 1,
      "name": "Alta",
      "identifier": "alta",
      "description": "Приложение для пассажиров общественного транспорта",
      "status": 1,
      "created_on": "2024-01-01T00:00:00Z",
      "updated_on": "2025-10-19T00:00:00Z"
    }
  ],
  "total_count": 1,
  "offset": 0,
  "limit": 25
}
```

**Examples**:

```bash
# List all projects
"$REDMINE_TOOL" list-projects

# Get project names and IDs
"$REDMINE_TOOL" list-projects | jq -r '.projects[] | "\(.id): \(.name)"'

# Find project ID by name
"$REDMINE_TOOL" list-projects | jq -r '.projects[] | select(.name == "Alta") | .id'
```

**Exit Codes**:

- 0: Success
- 1: Error (API error or authentication failure)

---

## Command: get-current-user

**Purpose**: Retrieve information about the currently authenticated user.

**Usage**:

```bash
"$REDMINE_TOOL" get-current-user
```

**Output** (JSON):

```json
{
  "user": {
    "id": 1,
    "login": "admin",
    "admin": true,
    "firstname": "Alexander",
    "lastname": "Kim",
    "mail": "avxkim@gmail.com",
    "created_on": "2024-01-01T00:00:00Z",
    "last_login_on": "2025-10-19T08:00:00Z",
    "api_key": "e668502d3cdd5019d56c6f2606f59af88a3461f3"
  }
}
```

**Examples**:

```bash
# Get current user info
"$REDMINE_TOOL" get-current-user

# Get user ID for filtering
USER_ID=$("$REDMINE_TOOL" get-current-user | jq -r '.user.id')

# Verify API key is working
"$REDMINE_TOOL" get-current-user | jq -r '.user.login'
```

**Exit Codes**:

- 0: Success
- 1: Error (invalid API key or authentication failure)

---

## Command: list-users

**Purpose**: Retrieve a list of users with optional status filtering.

**Usage**:

```bash
"$REDMINE_TOOL" list-users [OPTIONS]
```

**Options**:

- `--status <STATUS>`: Filter by status (1/active, 2/registered, 3/locked)
- `--name <NAME>`: Filter by name (substring match)
- `--limit <N>`: Maximum number of users to return (default: 100)
- `--offset <N>`: Pagination offset (default: 0)

**Status Values**:

- `1` or `active`: Active users
- `2` or `registered`: Registered but not activated users
- `3` or `locked`: Locked/inactive users

**Output** (JSON):

```json
{
  "users": [
    {
      "id": 1,
      "login": "admin",
      "admin": true,
      "firstname": "Alexander",
      "lastname": "Kim",
      "mail": "avxkim@gmail.com",
      "created_on": "2024-01-01T00:00:00Z",
      "last_login_on": "2025-10-19T08:00:00Z",
      "status": 1
    }
  ],
  "total_count": 13,
  "offset": 0,
  "limit": 100
}
```

**Examples**:

```bash
# List all users
"$REDMINE_TOOL" list-users

# List only active users
"$REDMINE_TOOL" list-users --status active

# List locked/inactive users
"$REDMINE_TOOL" list-users --status locked

# Search users by name
"$REDMINE_TOOL" list-users --name "Kim"

# Get user count by status
"$REDMINE_TOOL" list-users --status active | jq '.total_count'

# Extract user IDs and logins
"$REDMINE_TOOL" list-users | jq -r '.users[] | "\(.id): \(.login) (\(.firstname) \(.lastname))"'

# Find inactive users
"$REDMINE_TOOL" list-users --status 3 | jq -r '.users[] | "\(.id)\t\(.login)\t\(.mail)"'
```

**Exit Codes**:

- 0: Success
- 1: Error (API error or authentication failure)

---

## Command: get-wiki

**Purpose**: Retrieve wiki page content from Redmine.

**Usage**:

```bash
# Using URL
"$REDMINE_TOOL" get-wiki --url "https://redmine.example.com/projects/PROJECT/wiki/PAGE"

# Using project ID and page name
"$REDMINE_TOOL" get-wiki --project-id PROJECT --page PAGE_NAME
```

**Options**:

- `--url <URL>`: Full Redmine wiki page URL
- `--project-id <ID>`: Project identifier
- `--page <NAME>`: Wiki page name
- `--format <FORMAT>`: Output format ('text' or 'json', default: text)

**Note**: Either `--url` OR both `--project-id` and `--page` must be provided.

**Output** (Text format - default):

```
Title: Release 003
Project: alta
Page: Release-003
Version: 12
Author: Alexander Kim
Updated: 2025-10-15T10:30:00Z
--------------------------------------------------------------------------------
[Wiki page content in Textile/Markdown format...]
```

**Output** (JSON format):

```json
{
  "wiki_page": {
    "title": "Release 003",
    "text": "[Wiki page content...]",
    "version": 12,
    "author": {
      "id": 1,
      "name": "Alexander Kim"
    },
    "comments": "Updated release notes",
    "created_on": "2025-10-01T09:00:00Z",
    "updated_on": "2025-10-15T10:30:00Z"
  }
}
```

**Examples**:

```bash
# Read wiki page from URL (most common use case)
"$REDMINE_TOOL" get-wiki --url "https://redmine.int-tro.kz/projects/alta/wiki/Release-003"

# Read wiki page by project and page name
"$REDMINE_TOOL" get-wiki --project-id alta --page Release-003

# Get raw JSON for processing
"$REDMINE_TOOL" get-wiki --url "https://redmine.int-tro.kz/projects/alta/wiki/Tasks" --format json

# Extract just the content
"$REDMINE_TOOL" get-wiki --url "https://redmine.int-tro.kz/projects/alta/wiki/Tasks" --format json | jq -r '.wiki_page.text'

# Save wiki page to file
"$REDMINE_TOOL" get-wiki --url "https://redmine.int-tro.kz/projects/alta/wiki/Documentation" > wiki_content.txt
```

**Exit Codes**:

- 0: Success
- 1: Error (invalid URL, page not found, or API error)

**Common Use Cases**:

1. **Extract release tasks from wiki**:

   ```bash
   "$REDMINE_TOOL" get-wiki --url "https://redmine.int-tro.kz/projects/alta/wiki/Release-003"
   ```

2. **Convert wiki to another format**:

   ```bash
   "$REDMINE_TOOL" get-wiki --url "..." --format json | jq -r '.wiki_page.text' | pandoc -f textile -t markdown
   ```

3. **Check wiki page version**:
   ```bash
   "$REDMINE_TOOL" get-wiki --url "..." --format json | jq -r '.wiki_page.version'
   ```

---

## Error Handling

All commands follow consistent error handling:

- **Exit Code 0**: Successful execution
- **Exit Code 1**: Error occurred
- **Error messages**: Sent to stderr
- **Valid output**: Sent to stdout as JSON

**Common Error Messages**:

```
Error: REDMINE_API_KEY environment variable not set
HTTP Error 401: Unauthorized
HTTP Error 403: Forbidden
HTTP Error 404: Not Found
HTTP Error 422: Unprocessable Entity (validation error)
JSON Decode Error: ...
URL Error: ...
```

**Example Error Handling**:

```bash
if ! OUTPUT=$("$REDMINE_TOOL" get-issue 9999 2>/dev/null); then
    echo "Failed to get issue"
    exit 1
fi

echo "$OUTPUT" | jq '.'
```

---

## Best Practices

1. **Always use heredoc for JSON input**: Prevents escaping issues
2. **Check exit codes**: Use `if !` or `set -e` for error handling
3. **Pipe to jq**: Parse JSON output for specific fields
4. **Store API key securely**: Use environment variables, not hardcoded
5. **Use `--month current`**: Easier than calculating date ranges
6. **Limit large queries**: Use `--limit` to prevent timeouts
7. **Validate dates**: Use ISO format YYYY-MM-DD

---

## Common Workflows

### Daily Time Logging

```bash
# Log today's work
cat <<'EOF' | "$REDMINE_TOOL" log-time -
{
  "issue_id": 564,
  "hours": 6.5,
  "activity_id": 9,
  "comments": "Implemented feature X, fixed bug Y"
}
EOF
```

### Monthly Reporting

```bash
# Generate report for current month
"$REDMINE_TOOL" time-report --month current > report.md

# Email to manager
cat report.md | mail -s "Monthly Time Report" manager@example.com
```

### Issue Management

```bash
# Create issue, log time, close it
ISSUE_ID=$(cat <<'EOF' | "$REDMINE_TOOL" create-issue - | jq -r '.issue.id'
{"project_id": 1, "subject": "Quick fix"}
EOF
)

cat <<EOF | "$REDMINE_TOOL" log-time -
{"issue_id": $ISSUE_ID, "hours": 0.5, "comments": "Applied fix"}
EOF

cat <<EOF | "$REDMINE_TOOL" update-issue $ISSUE_ID -
{"status_id": 5, "done_ratio": 100}
EOF
```
