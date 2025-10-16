#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/auto-format.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
    echo "[HOOK] $*" >&2
}

log "Auto-format hook triggered"

hook_data=$(cat)
log "Hook data received (first 200 chars): ${hook_data:0:200}..."

file_path=$(echo "$hook_data" | jq -r '.toolOutput.file // .toolOutput.path // .toolOutput.file_path // .tool_input.file_path // empty')

log "Extracted file_path: $file_path"

if [ -z "$file_path" ]; then
    log "No file_path found in hook data"
    exit 0
fi

if [ ! -f "$file_path" ]; then
    log "File does not exist: $file_path"
    exit 0
fi

log "Processing file: $file_path"

case "$file_path" in
    *.js|*.jsx|*.ts|*.tsx|*.vue|*.mjs|*.cjs)
        log "Running prettier + eslint on JS/TS file"
        npx prettier --write "$file_path" 2>/dev/null || true
        npx eslint --fix "$file_path" 2>/dev/null || true
        ;;
    *.py)
        log "Running black + isort on Python file"
        black "$file_path" 2>/dev/null || true
        isort "$file_path" 2>/dev/null || true
        ;;
    *.rs)
        log "Running rustfmt on Rust file"
        rustfmt "$file_path" 2>/dev/null || true
        ;;
    *.go)
        log "Running gofmt + goimports on Go file"
        gofmt -w "$file_path" 2>/dev/null || true
        goimports -w "$file_path" 2>/dev/null || true
        ;;
    *.rb)
        log "Running rubocop on Ruby file"
        rubocop -A "$file_path" 2>/dev/null || true
        ;;
    *.php)
        log "Running php-cs-fixer on PHP file"
        php-cs-fixer fix "$file_path" 2>/dev/null || true
        ;;
    *.java)
        log "Running google-java-format on Java file"
        google-java-format -i "$file_path" 2>/dev/null || true
        ;;
    *.css|*.scss|*.sass|*.less)
        log "Running prettier on CSS file"
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.html|*.htm)
        log "Running prettier on HTML file"
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.json)
        log "Running prettier on JSON file"
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.yml|*.yaml)
        log "Running prettier on YAML file"
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.md|*.markdown)
        log "Running prettier on Markdown file"
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.dart)
        log "Running dart format on Dart file"
        dart format "$file_path" 2>/dev/null || true
        ;;
    *.swift)
        log "Running swift-format on Swift file"
        swift-format -i "$file_path" 2>/dev/null || true
        ;;
    *.kt)
        log "Running ktlint on Kotlin file"
        ktlint -F "$file_path" 2>/dev/null || true
        ;;
    *.sql)
        log "Running sqlfluff/pg_format on SQL file"
        (sqlfluff fix "$file_path" || pg_format -i "$file_path") 2>/dev/null || true
        ;;
    *)
        log "No formatter configured for this file type"
        ;;
esac

file_name=$(basename "$file_path")
log "Successfully auto-formatted: $file_name"
echo ""
echo "✅ Auto-formatted: $file_name"
echo ""

exit 0
