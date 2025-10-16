#!/bin/bash

file_path=$(echo "$HOOK_INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$file_path" ] || [ ! -f "$file_path" ]; then
    exit 0
fi

case "$file_path" in
    *.js|*.jsx|*.ts|*.tsx|*.vue|*.mjs|*.cjs)
        npx prettier --write "$file_path" 2>/dev/null || true
        npx eslint --fix "$file_path" 2>/dev/null || true
        ;;
    *.py)
        black "$file_path" 2>/dev/null || true
        isort "$file_path" 2>/dev/null || true
        ;;
    *.rs)
        rustfmt "$file_path" 2>/dev/null || true
        ;;
    *.go)
        gofmt -w "$file_path" 2>/dev/null || true
        goimports -w "$file_path" 2>/dev/null || true
        ;;
    *.rb)
        rubocop -A "$file_path" 2>/dev/null || true
        ;;
    *.php)
        php-cs-fixer fix "$file_path" 2>/dev/null || true
        ;;
    *.java)
        google-java-format -i "$file_path" 2>/dev/null || true
        ;;
    *.css|*.scss|*.sass|*.less)
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.html|*.htm)
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.json)
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.yml|*.yaml)
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.md|*.markdown)
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.dart)
        dart format "$file_path" 2>/dev/null || true
        ;;
    *.swift)
        swift-format -i "$file_path" 2>/dev/null || true
        ;;
    *.kt)
        ktlint -F "$file_path" 2>/dev/null || true
        ;;
    *.sql)
        (sqlfluff fix "$file_path" || pg_format -i "$file_path") 2>/dev/null || true
        ;;
esac

file_name=$(basename "$file_path")
echo "✓ Auto-formatted: $file_name"

exit 0
