# Redmine Admin Scripts

Python scripts for Redmine REST API operations.

## Core Module

- **redmine_api.py** - Base API client with authentication and HTTP request handling

## Available Scripts

| Script              | Purpose                     | Usage                               |
| ------------------- | --------------------------- | ----------------------------------- |
| list_issues.py      | List issues with filters    | `--project-id 1 --status-id open`   |
| get_issue.py        | Get issue details           | `<ISSUE_ID>`                        |
| create_issue.py     | Create new issue            | Reads JSON from stdin               |
| update_issue.py     | Update existing issue       | `<ISSUE_ID> -` (JSON from stdin)    |
| log_time.py         | Log time entry              | Reads JSON from stdin               |
| get_time_entries.py | Retrieve time entries       | `--month current --user-id me`      |
| time_report.py      | Generate time reports       | `--month 2025-10 --format markdown` |
| list_projects.py    | List all projects           | No arguments                        |
| get_current_user.py | Get authenticated user info | No arguments                        |

## Authentication

All scripts require these environment variables:

- `REDMINE_API_KEY` - Your Redmine API key
- `REDMINE_URL` - Redmine instance URL

## Common Patterns

All scripts:

- Return JSON output to stdout
- Send errors to stderr
- Exit with code 0 on success, 1 on error
- Use Python 3 standard library only (no external dependencies)

Scripts that accept JSON input use stdin with `-` argument:

- create_issue.py
- update_issue.py
- log_time.py

## Error Handling

Common error scenarios:

- Missing `REDMINE_API_KEY`: Exit 1 with error message
- HTTP 401: Invalid API key
- HTTP 403: Permission denied
- HTTP 404: Resource not found
- HTTP 422: Validation error

## Development

All scripts are standalone and can be run directly:

```bash
python3 get_current_user.py
python3 list_issues.py --project-id 1
```

Or via the wrapper script:

```bash
./redmine-tool.sh get-current-user
./redmine-tool.sh list-issues --project-id 1
```
