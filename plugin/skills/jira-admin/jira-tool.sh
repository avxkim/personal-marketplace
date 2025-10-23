#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

command="$1"
shift

case "$command" in
    discover)
        python3 "$SCRIPTS_DIR/discover.py" "$@"
        ;;
    jira-search)
        python3 "$SCRIPTS_DIR/jira_search_issues.py" "$@"
        ;;
    jira-get-issue)
        python3 "$SCRIPTS_DIR/jira_get_issue.py" "$@"
        ;;
    jira-create-issue)
        python3 "$SCRIPTS_DIR/jira_create_issue.py" "$@"
        ;;
    jira-update-issue)
        python3 "$SCRIPTS_DIR/jira_update_issue.py" "$@"
        ;;
    jira-list-sprints)
        python3 "$SCRIPTS_DIR/jira_list_sprints.py" "$@"
        ;;
    jira-get-sprint)
        python3 "$SCRIPTS_DIR/jira_get_sprint.py" "$@"
        ;;
    --help|-h|help)
        echo "Jira Admin Tool - Manage Jira via REST API"
        echo ""
        echo "Discovery:"
        echo "  discover                    - List all Jira instances"
        echo ""
        echo "Jira:"
        echo "  jira-search                 - Search/list issues with JQL"
        echo "  jira-get-issue              - Get issue details"
        echo "  jira-create-issue           - Create new issue"
        echo "  jira-update-issue           - Update issue"
        echo "  jira-list-sprints           - List sprints for board"
        echo "  jira-get-sprint             - Get sprint details"
        echo ""
        echo "  --help, -h, help            - Show this message"
        exit 0
        ;;
    *)
        echo "Unknown command: $command" >&2
        echo "Use --help for available commands" >&2
        exit 1
        ;;
esac
