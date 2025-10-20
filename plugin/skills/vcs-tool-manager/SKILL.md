---
name: VCS Tool Manager
description: Resolves head commit SHAs from GitHub/GitLab and generates validated per-line blob URLs for reliable code review linking. Uses gh/glab; always tests links via curl. Use when working with MRs/PRs, generating code review links, or when needing to reference specific lines in version control systems.
allowed-tools: Bash, Read, Grep, WebFetch, BashOutput, KillShell
---

# VCS Tool Manager

This skill provides utilities for working with GitLab and GitHub version control systems, specifically focused on generating accurate file links for code reviews.

## Core Capabilities

1. **Platform Detection**: Automatically detect GitHub vs GitLab
2. **Extract MR/PR Metadata**: Retrieve source branch, commit SHA, and repository details
3. **Find Line Numbers**: Accurate absolute line numbers (not git diff positions)
4. **Generate Blob URLs**: Create properly formatted URLs with line numbers
5. **Format Reviews**: Consistent markdown formatting from JSON
6. **Validate URLs**: Test links via curl to ensure they're accessible

## When to Use This Skill

Invoke this skill when you need to:

- Generate file links for GitLab merge request reviews
- Generate file links for GitHub pull request reviews
- Reference specific code lines in version control comments
- Find accurate line numbers for code review feedback
- Format code review or architecture review comments consistently
- Ensure code review links are valid before posting

## Finding the Plugin Location

**IMPORTANT**: Before using this skill's scripts, locate the vcs-tool wrapper.

**Method 1: Auto-discover (works with any marketplace name)**

```bash
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)
```

**Method 2: Direct lookup (faster, requires knowing marketplace name)**

```bash
VCS_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/vcs-tool-manager/vcs-tool.sh
```

All commands below use `$VCS_TOOL` as the entry point.

## Quick Command Reference

All commands are invoked via the `vcs-tool.sh` wrapper script.

### 1. Detect Platform (Run First)

```bash
PLATFORM=$("$VCS_TOOL" detect-platform)  # Returns: github or gitlab
```

### 2. Get MR/PR Metadata

```bash
# GitLab
METADATA=$("$VCS_TOOL" get-gitlab-mr <MR_NUMBER>)

# GitHub
METADATA=$("$VCS_TOOL" get-github-pr <PR_NUMBER>)
```

Returns JSON with host/namespace/repo/branch/sha/url.

### 3. Find Line Number (Recommended for Code Reviews)

```bash
"$VCS_TOOL" find-line <file_path> <pattern> [context_hint] [--method|--regex]
```

Returns JSON with accurate absolute line number (not git diff position).

**Why use this?** Git diff shows relative positions like `@@ -258,5 +258,5 @@`, not actual file line numbers. This script reads the actual file and returns the correct line.

**Examples:**

```bash
# Find exact line for method call
"$VCS_TOOL" find-line src/Service.java "updateRouteDeviationNotification"

# Find method definition
"$VCS_TOOL" find-line src/Service.java "createRouteUnits" --method

# Disambiguate with context
"$VCS_TOOL" find-line src/Service.java "save" "createRouteUnits"
```

### 4. Format Blob URL

```bash
URL_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"$PLATFORM\", file_path: \"$FILE_PATH\", line_number: $LINE_NUMBER}")
URL=$("$VCS_TOOL" format-url "$URL_INPUT")
```

Generates: `https://gitlab.com/org/repo/-/blob/SHA/path/file.ts#L42`

**Note**: Always uses commit SHA (not branch names) for permanent, reliable links.

### 5. Validate URL

```bash
"$VCS_TOOL" validate-url <URL>  # Tests via curl, returns HTTP status
```

### 6. Format Review Comment

**CRITICAL**: Never pass JSON as command-line argument - always use stdin!

**Pattern A: JSON in a variable (typical agent output scenario)**

```bash
# When you have JSON from agent in a variable
CODE_REVIEW_JSON='{"type":"code",...}'

# Use printf (NOT echo) to avoid backtick interpretation
CODE_COMMENT=$(printf '%s' "$CODE_REVIEW_JSON" | "$VCS_TOOL" format-review -)

# Same for architecture review
ARCH_REVIEW_JSON='{"type":"architecture",...}'
ARCH_COMMENT=$(printf '%s' "$ARCH_REVIEW_JSON" | "$VCS_TOOL" format-review -)
```

**Pattern B: Literal JSON (for examples/testing)**

```bash
# Use heredoc with single quotes for literal JSON
CODE_COMMENT=$(cat <<'EOF_CODE' | "$VCS_TOOL" format-review -
{
  "type": "code",
  "verdict": "PASS",
  "critical": [...],
  "warnings": [...],
  "suggestions": [...]
}
EOF_CODE
)
```

**Why `printf '%s'` instead of `echo`?**

- Prevents bash from interpreting backticks in JSON as command substitution
- Outputs variable exactly as-is without escape sequence interpretation
- Essential when JSON contains code snippets with backticks

### 7. Post Comment to MR/PR

```bash
# Method 1: Pass comment directly (for short comments)
"$VCS_TOOL" post-comment <platform> <issue_number> "Comment text"

# Method 2: Use stdin with heredoc (recommended for long comments)
cat <<'EOF' | "$VCS_TOOL" post-comment <platform> <issue_number> -
Your long comment text here...
Can span multiple lines...
EOF
```

**Parameters**:

- `platform`: "gitlab" or "github"
- `issue_number`: MR/PR number (e.g., "123")
- `comment`: Comment text (use `-` to read from stdin)

**Examples**:

```bash
# GitLab MR
"$VCS_TOOL" post-comment gitlab 123 "LGTM! Ready to merge."

# GitHub PR with long comment
cat <<'EOF' | "$VCS_TOOL" post-comment github 456 -
# Code Review Summary

## Critical Issues
...
EOF
```

## Complete Workflow Example

```bash
# Locate tool
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

# Detect platform
PLATFORM=$("$VCS_TOOL" detect-platform)

# Get metadata (auto-detect GitLab vs GitHub)
if [ "$PLATFORM" = "gitlab" ]; then
    METADATA=$("$VCS_TOOL" get-gitlab-mr "123")
else
    METADATA=$("$VCS_TOOL" get-github-pr "123")
fi

# Find accurate line number
RESULT=$("$VCS_TOOL" find-line "src/Service.java" "methodName")
LINE=$(echo "$RESULT" | jq -r '.line')

# Generate URL
URL_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"$PLATFORM\", file_path: \"src/Service.java\", line_number: $LINE}")
URL=$("$VCS_TOOL" format-url "$URL_INPUT")

# Validate before using
"$VCS_TOOL" validate-url "$URL"
```

## Additional Documentation

- **[commands.md](commands.md)** - Detailed command reference with full JSON schemas, exit codes, and parameters
- **[examples.md](examples.md)** - Complete workflow examples for common scenarios
- **[troubleshooting.md](troubleshooting.md)** - Common pitfalls, best practices, and error solutions

## Prerequisites

- **GitLab**: `glab` CLI tool installed and authenticated
- **GitHub**: `gh` CLI tool installed and authenticated
- **Git**: Working git repository with configured remote
- **Python 3**: For running scripts
- **jq**: For JSON processing in bash workflows
- **curl**: For URL validation

## Integration with Code Review Workflows

This skill is designed to work seamlessly with the `code-reviewer` and `software-architect` agents:

1. Agents invoke this skill to generate file links
2. Metadata extraction happens before analysis
3. Line numbers are found using `find-line` command (not git diff)
4. URLs are validated before posting comments to MR/PR
5. Review formatting uses `format-review` for consistency

## Key Points

✅ **Always use commit SHA** - not branch names (permanent links)
✅ **Always use find-line** - not git diff line numbers (accurate positions)
✅ **Always use heredoc** - for format-review (avoid escaping errors)
✅ **Always detect platform first** - before calling MR/PR commands

---

**For detailed command documentation, see [commands.md](commands.md)**
