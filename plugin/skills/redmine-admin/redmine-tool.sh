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
    *)
        echo "Unknown command: $command" >&2
        echo "Available commands: list-issues, get-issue, create-issue, update-issue, log-time, get-time-entries, time-report, list-projects, get-current-user" >&2
        exit 1
        ;;
esac
