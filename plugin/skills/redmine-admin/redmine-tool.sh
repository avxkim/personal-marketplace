#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

command="$1"
shift

case "$command" in
    list-issues)
        python3 "$SCRIPTS_DIR/list_issues.py" "$@"
        ;;
    get-issue)
        python3 "$SCRIPTS_DIR/get_issue.py" "$@"
        ;;
    create-issue)
        python3 "$SCRIPTS_DIR/create_issue.py" "$@"
        ;;
    update-issue)
        python3 "$SCRIPTS_DIR/update_issue.py" "$@"
        ;;
    log-time)
        python3 "$SCRIPTS_DIR/log_time.py" "$@"
        ;;
    get-time-entries)
        python3 "$SCRIPTS_DIR/get_time_entries.py" "$@"
        ;;
    time-report)
        python3 "$SCRIPTS_DIR/time_report.py" "$@"
        ;;
    list-projects)
        python3 "$SCRIPTS_DIR/list_projects.py" "$@"
        ;;
    get-current-user)
        python3 "$SCRIPTS_DIR/get_current_user.py" "$@"
        ;;
    list-users)
        python3 "$SCRIPTS_DIR/list_users.py" "$@"
        ;;
    get-wiki)
        python3 "$SCRIPTS_DIR/get_wiki.py" "$@"
        ;;
    --help|-h|help)
        echo "Available commands:"
        echo "  list-issues       - List issues with optional filters"
        echo "  get-issue         - Get detailed information about an issue"
        echo "  create-issue      - Create a new issue"
        echo "  update-issue      - Update an existing issue"
        echo "  log-time          - Log time entry for an issue"
        echo "  get-time-entries  - Get time entries with filters"
        echo "  time-report       - Generate time report"
        echo "  list-projects     - List all projects"
        echo "  get-current-user  - Get current authenticated user"
        echo "  list-users        - List users with optional status filter"
        echo "  get-wiki          - Get wiki page content by URL or project/page"
        echo "  --help, -h, help  - Show this help message"
        exit 0
        ;;
    *)
        echo "Unknown command: $command" >&2
        echo "Available commands: list-issues, get-issue, create-issue, update-issue, log-time, get-time-entries, time-report, list-projects, get-current-user, list-users, get-wiki" >&2
        echo "Use --help for more information" >&2
        exit 1
        ;;
esac
