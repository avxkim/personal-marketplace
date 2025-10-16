#!/bin/bash

file_path=$(echo "$HOOK_INPUT" | jq -r '.cwd // empty')
cd "$file_path" 2>/dev/null || exit 0

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    exit 0
fi

if git diff --quiet HEAD 2>/dev/null && git diff --quiet --cached 2>/dev/null; then
    exit 0
fi

output=$(cat <<'EOF'
{
  "continue": true,
  "stopReason": "Code changes detected. Running code-reviewer and documentarian agents before completing.",
  "systemMessage": "⚠️ Code changes detected. Launching code-reviewer and documentarian agents..."
}
EOF
)

echo "$output"
exit 0
