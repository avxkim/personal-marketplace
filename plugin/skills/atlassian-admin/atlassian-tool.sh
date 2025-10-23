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
    confluence-get-page)
        python3 "$SCRIPTS_DIR/confluence_get_page.py" "$@"
        ;;
    confluence-search)
        python3 "$SCRIPTS_DIR/confluence_search.py" "$@"
        ;;
    confluence-create-page)
        python3 "$SCRIPTS_DIR/confluence_create_page.py" "$@"
        ;;
    confluence-update-page)
        python3 "$SCRIPTS_DIR/confluence_update_page.py" "$@"
        ;;
    confluence-list-spaces)
        python3 "$SCRIPTS_DIR/confluence_list_spaces.py" "$@"
        ;;
    confluence-list-pages)
        python3 "$SCRIPTS_DIR/confluence_list_pages.py" "$@"
        ;;
    --help|-h|help)
        echo "Atlassian Admin Tool - Manage Jira and Confluence"
        echo ""
        echo "Discovery:"
        echo "  discover                    - List all Jira/Confluence instances"
        echo ""
        echo "Jira:"
        echo "  jira-search                 - Search/list issues with JQL"
        echo "  jira-get-issue              - Get issue details"
        echo "  jira-create-issue           - Create new issue"
        echo "  jira-update-issue           - Update issue"
        echo "  jira-list-sprints           - List sprints for board"
        echo "  jira-get-sprint             - Get sprint details"
        echo ""
        echo "Confluence:"
        echo "  confluence-get-page         - Get page by URL or space/title"
        echo "  confluence-search           - Search using CQL"
        echo "  confluence-create-page      - Create new page"
        echo "  confluence-update-page      - Update page"
        echo "  confluence-list-spaces      - List all spaces"
        echo "  confluence-list-pages       - List pages in space"
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
