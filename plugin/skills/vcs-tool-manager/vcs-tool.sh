#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

command="$1"
shift

case "$command" in
    detect-platform)
        python3 "$SCRIPTS_DIR/detect_platform.py" "$@"
        ;;
    get-gitlab-mr)
        python3 "$SCRIPTS_DIR/get_gitlab_mr_metadata.py" "$@"
        ;;
    get-github-pr)
        python3 "$SCRIPTS_DIR/get_github_pr_metadata.py" "$@"
        ;;
    format-url)
        python3 "$SCRIPTS_DIR/format_blob_url.py" "$@"
        ;;
    validate-url)
        python3 "$SCRIPTS_DIR/validate_url.py" "$@"
        ;;
    find-line)
        python3 "$SCRIPTS_DIR/find_line_number.py" "$@"
        ;;
    *)
        echo "Unknown command: $command" >&2
        echo "Available commands: detect-platform, get-gitlab-mr, get-github-pr, format-url, validate-url, find-line" >&2
        exit 1
        ;;
esac
