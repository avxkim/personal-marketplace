#!/bin/bash

if ! command -v jq >/dev/null 2>&1; then
    exit 0
fi

hook_data=$(cat)

file_path=$(echo "$hook_data" | jq -r '.toolOutput.file // .toolOutput.path // .toolOutput.file_path // .tool_input.file_path // empty')

if [ -z "$file_path" ]; then
    exit 0
fi

if [ ! -f "$file_path" ]; then
    exit 0
fi

file_name=$(basename "$file_path")

formatter_msg=""

case "$file_path" in
    *.js|*.jsx|*.ts|*.tsx|*.vue|*.mjs|*.cjs)
        project_root=$(git rev-parse --show-toplevel 2>/dev/null)

        if [ -n "$project_root" ] && [ -f "$project_root/node_modules/.bin/prettier" ]; then
            (cd "$project_root" && ./node_modules/.bin/prettier --write "$file_path") 2>/dev/null || true
        else
            npx prettier --write "$file_path" 2>/dev/null || true
        fi

        if [ -n "$project_root" ] && [ -f "$project_root/node_modules/.bin/eslint" ]; then
            (cd "$project_root" && ./node_modules/.bin/eslint --fix "$file_path") 2>/dev/null || true
        else
            npx eslint --fix "$file_path" 2>/dev/null || true
        fi

        formatter_msg="prettier + eslint"
        ;;
    *.py)
        black "$file_path" 2>/dev/null || true
        isort "$file_path" 2>/dev/null || true
        formatter_msg="black + isort"
        ;;
    *.rs)
        rustfmt "$file_path" 2>/dev/null || true
        formatter_msg="rustfmt"
        ;;
    *.go)
        gofmt -w "$file_path" 2>/dev/null || true
        goimports -w "$file_path" 2>/dev/null || true
        formatter_msg="gofmt + goimports"
        ;;
    *.rb)
        rubocop -A "$file_path" 2>/dev/null || true
        formatter_msg="rubocop"
        ;;
    *.php)
        php-cs-fixer fix "$file_path" 2>/dev/null || true
        formatter_msg="php-cs-fixer"
        ;;
    *.java)
        google-java-format -i "$file_path" 2>/dev/null || true
        formatter_msg="google-java-format"
        ;;
    *.css|*.scss|*.sass|*.less|*.html|*.htm|*.json|*.yml|*.yaml|*.md|*.markdown)
        project_root=$(git rev-parse --show-toplevel 2>/dev/null)

        if [ -n "$project_root" ] && [ -f "$project_root/node_modules/.bin/prettier" ]; then
            (cd "$project_root" && ./node_modules/.bin/prettier --write "$file_path") 2>/dev/null || true
        else
            npx prettier --write "$file_path" 2>/dev/null || true
        fi

        formatter_msg="prettier"
        ;;
    *.dart)
        dart format "$file_path" 2>/dev/null || true
        formatter_msg="dart format"
        ;;
    *.swift)
        swift-format -i "$file_path" 2>/dev/null || true
        formatter_msg="swift-format"
        ;;
    *.kt)
        ktlint -F "$file_path" 2>/dev/null || true
        formatter_msg="ktlint"
        ;;
    *.sql)
        (sqlfluff fix "$file_path" || pg_format -i "$file_path") 2>/dev/null || true
        formatter_msg="sqlfluff/pg_format"
        ;;
    *)
        exit 0
        ;;
esac

if [ -n "$formatter_msg" ]; then
    jq -n --arg reason "Formatted $file_name with $formatter_msg" '{reason: $reason}'
fi

exit 0
