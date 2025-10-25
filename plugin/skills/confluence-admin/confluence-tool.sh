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
    list-spaces)
        python3 "$SCRIPTS_DIR/confluence_list_spaces.py" "$@"
        ;;
    get-space)
        python3 "$SCRIPTS_DIR/confluence_get_space.py" "$@"
        ;;
    get-page)
        python3 "$SCRIPTS_DIR/confluence_get_page.py" "$@"
        ;;
    search)
        python3 "$SCRIPTS_DIR/confluence_search.py" "$@"
        ;;
    create-page)
        python3 "$SCRIPTS_DIR/confluence_create_page.py" "$@"
        ;;
    update-page)
        python3 "$SCRIPTS_DIR/confluence_update_page.py" "$@"
        ;;
    list-attachments)
        python3 "$SCRIPTS_DIR/confluence_list_attachments.py" "$@"
        ;;
    --help|-h|help)
        echo "Confluence Admin Tool - Manage Confluence via REST API"
        echo ""
        echo "Discovery:"
        echo "  discover                      - List all Confluence instances"
        echo ""
        echo "Spaces:"
        echo "  list-spaces <instance> [limit] [type]"
        echo "                                - List spaces (type: global/personal/all)"
        echo "  get-space <instance> <key>    - Get space details"
        echo ""
        echo "Pages:"
        echo "  get-page <instance> <id> [expand]"
        echo "                                - Get page by ID"
        echo "  search <instance> <cql> [limit]"
        echo "                                - Search with CQL"
        echo "  create-page <instance> <json|->"
        echo "                                - Create new page"
        echo "  update-page <instance> <id> <json|->"
        echo "                                - Update page"
        echo ""
        echo "Attachments:"
        echo "  list-attachments <instance> <page_id> [limit]"
        echo "                                - List page attachments"
        echo ""
        echo "  --help, -h, help              - Show this message"
        exit 0
        ;;
    *)
        echo "Unknown command: $command" >&2
        echo "Use --help for available commands" >&2
        exit 1
        ;;
esac
