#!/bin/bash

echo "[HOOK] Auto-format hook triggered" >&2
echo "[HOOK] HOOK_INPUT: $HOOK_INPUT" >&2

file_path=$(echo "$HOOK_INPUT" | jq -r '.tool_input.file_path // empty')

echo "[HOOK] Extracted file_path: $file_path" >&2

if [ -z "$file_path" ]; then
    echo "[HOOK] No file_path found in HOOK_INPUT" >&2
    exit 0
fi

if [ ! -f "$file_path" ]; then
    echo "[HOOK] File does not exist: $file_path" >&2
    exit 0
fi

echo "[HOOK] Processing file: $file_path" >&2

case "$file_path" in
    *.js|*.jsx|*.ts|*.tsx|*.vue|*.mjs|*.cjs)
        echo "[HOOK] Running prettier + eslint" >&2
        npx prettier --write "$file_path" 2>/dev/null || true
        npx eslint --fix "$file_path" 2>/dev/null || true
        ;;
    *.py)
        echo "[HOOK] Running black + isort" >&2
        black "$file_path" 2>/dev/null || true
        isort "$file_path" 2>/dev/null || true
        ;;
    *.rs)
        echo "[HOOK] Running rustfmt" >&2
        rustfmt "$file_path" 2>/dev/null || true
        ;;
    *.go)
        echo "[HOOK] Running gofmt + goimports" >&2
        gofmt -w "$file_path" 2>/dev/null || true
        goimports -w "$file_path" 2>/dev/null || true
        ;;
    *.rb)
        echo "[HOOK] Running rubocop" >&2
        rubocop -A "$file_path" 2>/dev/null || true
        ;;
    *.php)
        echo "[HOOK] Running php-cs-fixer" >&2
        php-cs-fixer fix "$file_path" 2>/dev/null || true
        ;;
    *.java)
        echo "[HOOK] Running google-java-format" >&2
        google-java-format -i "$file_path" 2>/dev/null || true
        ;;
    *.css|*.scss|*.sass|*.less)
        echo "[HOOK] Running prettier" >&2
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.html|*.htm)
        echo "[HOOK] Running prettier" >&2
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.json)
        echo "[HOOK] Running prettier" >&2
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.yml|*.yaml)
        echo "[HOOK] Running prettier" >&2
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.md|*.markdown)
        echo "[HOOK] Running prettier" >&2
        npx prettier --write "$file_path" 2>/dev/null || true
        ;;
    *.dart)
        echo "[HOOK] Running dart format" >&2
        dart format "$file_path" 2>/dev/null || true
        ;;
    *.swift)
        echo "[HOOK] Running swift-format" >&2
        swift-format -i "$file_path" 2>/dev/null || true
        ;;
    *.kt)
        echo "[HOOK] Running ktlint" >&2
        ktlint -F "$file_path" 2>/dev/null || true
        ;;
    *.sql)
        echo "[HOOK] Running sqlfluff/pg_format" >&2
        (sqlfluff fix "$file_path" || pg_format -i "$file_path") 2>/dev/null || true
        ;;
    *)
        echo "[HOOK] No formatter configured for this file type" >&2
        ;;
esac

file_name=$(basename "$file_path")
echo "✓ Auto-formatted: $file_name" >&2
echo "✓ Auto-formatted: $file_name"

exit 0
