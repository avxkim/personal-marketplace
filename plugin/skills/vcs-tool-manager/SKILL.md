---
name: VCS Tool Manager
description: Resolves head commit SHAs from GitHub/GitLab and generates validated per-line blob URLs for reliable code review linking. Uses gh/glab; always tests links via curl. Use when working with MRs/PRs, generating code review links, or when needing to reference specific lines in version control systems.
allowed-tools: Bash, Read, Grep, WebFetch, BashOutput, KillShell
---

# VCS Tool Manager

This skill provides utilities for working with GitLab and GitHub version control systems, specifically focused on generating accurate file links for code reviews.

## Core Capabilities

1. **Extract MR/PR Metadata**: Retrieve source branch, commit SHA, and repository details
2. **Generate Blob URLs**: Create properly formatted URLs with line numbers
3. **Validate URLs**: Test links via curl to ensure they're accessible
4. **Handle Edge Cases**: Manage special characters in branch names (#, %, spaces)

## When to Use This Skill

Invoke this skill when you need to:

- Generate file links for GitLab merge request reviews
- Generate file links for GitHub pull request reviews
- Reference specific code lines in version control comments
- Ensure code review links are valid before posting
- Handle complex branch names with special characters

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

## Available Scripts

All scripts can be invoked via the `vcs-tool.sh` wrapper script.

### 0. Detect Platform (REQUIRED FIRST STEP)

**Script**: `detect_platform.py`

**Purpose**: Automatically detects whether the current repository is on GitHub or GitLab by analyzing the git remote URL.

**Usage**:

```bash
PLATFORM=$("$VCS_TOOL" detect-platform)
```

**Output**:

```
github
```

or

```
gitlab
```

**How It Works**:

1. Retrieves git remote URL from current repository
2. Checks if URL contains "github.com" → returns "github"
3. Checks if URL contains "gitlab" → returns "gitlab"
4. Exits with error if platform cannot be detected

**Exit Codes**:

- 0: Platform detected successfully
- 1: Error (could not get remote URL or unsupported platform)

**IMPORTANT**: Always run this script first before calling platform-specific metadata scripts. This ensures you use the correct script for your repository.

### 1. Get GitLab MR Metadata

**Script**: `get_gitlab_mr_metadata.py`

**Purpose**: Extracts metadata from a GitLab merge request including source branch, commit SHA, and repository details.

**Usage**:

```bash
"$VCS_TOOL" get-gitlab-mr <MR_NUMBER>
```

**Output** (JSON):

```json
{
  "host": "gitlab.example.com",
  "namespace": "myorg",
  "repo": "myrepo",
  "source_branch": "feature/add-authentication",
  "sha": "abc123def456",
  "web_url": "https://gitlab.example.com/myorg/myrepo/-/merge_requests/123"
}
```

**How It Works**:

1. Retrieves git remote URL from current repository
2. Parses GitLab host, namespace, and repo name
3. **Automatically sets `GITLAB_HOST` environment variable** for self-hosted instances
4. Fetches MR metadata using `glab mr view` command
5. Falls back to `glab api` if direct view fails

**Self-Hosted GitLab Support**:

- Automatically detects self-hosted GitLab instances from git remote
- Sets `GITLAB_HOST` environment variable before running `glab` commands
- No manual configuration needed - works for both gitlab.com and self-hosted

### 2. Get GitHub PR Metadata

**Script**: `get_github_pr_metadata.py`

**Purpose**: Extracts metadata from a GitHub pull request including head branch, commit SHA, and repository details.

**Usage**:

```bash
"$VCS_TOOL" get-github-pr <PR_NUMBER>
```

**Output** (JSON):

```json
{
  "owner": "myorg",
  "repo": "myrepo",
  "head_ref": "feature/add-authentication",
  "sha": "abc123def456",
  "web_url": "https://github.com/myorg/myrepo/pull/123"
}
```

**How It Works**:

1. Retrieves git remote URL from current repository
2. Parses GitHub owner and repo name
3. Fetches PR metadata using `gh pr view` command

### 3. Format Blob URL

**Script**: `format_blob_url.py`

**Purpose**: Generates properly formatted blob URLs with line numbers for both GitLab and GitHub.

**Usage**:

```bash
"$VCS_TOOL" format-url '<JSON_METADATA>'
```

**Input JSON** (GitLab):

```json
{
  "platform": "gitlab",
  "host": "gitlab.example.com",
  "namespace": "myorg",
  "repo": "myrepo",
  "file_path": "src/auth/login.ts",
  "line_number": 42,
  "sha": "abc123def456",
  "source_branch": "feature/add-authentication"
}
```

**Input JSON** (GitHub):

```json
{
  "platform": "github",
  "owner": "myorg",
  "repo": "myrepo",
  "file_path": "src/auth/login.ts",
  "line_number": 42,
  "sha": "abc123def456",
  "head_ref": "feature/add-authentication"
}
```

**Output**:

```
https://gitlab.example.com/myorg/myrepo/-/blob/abc123def456/src/auth/login.ts#L42
```

**URL Generation**:

- **Always uses commit SHA** for reliable, permanent links that won't break after branch deletion or updates
- URL-encodes file paths properly

### 4. Validate URL

**Script**: `validate_url.py`

**Purpose**: Tests URLs via curl to ensure they return valid HTTP status codes (200 or 302).

**Usage**:

```bash
"$VCS_TOOL" validate-url <URL>
```

**Output**:

```
URL: https://gitlab.example.com/myorg/myrepo/-/blob/abc123/file.ts#L42
Status: Valid
HTTP Code: 200
```

**Exit Codes**:

- 0: URL is valid (HTTP 200 or 302)
- 1: URL is invalid or unreachable

### 5. Find Line Number (RECOMMENDED for Code Reviews)

**Script**: `find_line_number.py`

**Purpose**: Finds accurate line numbers in source files for code patterns. This solves the problem of git diff showing relative positions instead of absolute file line numbers.

**Usage**:

```bash
"$VCS_TOOL" find-line <file_path> <pattern> [context_hint] [--method|--regex]
```

**Parameters**:

- `file_path`: Absolute or relative path to the source file
- `pattern`: Code snippet or pattern to search for (exact string match by default)
- `context_hint` (optional): Additional context to disambiguate multiple matches (e.g., method name)
- `--method`: Search for method/function definitions
- `--regex`: Use regex pattern matching instead of literal string

**Output** (JSON):

```json
{
  "found": true,
  "file": "src/main/java/Service.java",
  "pattern": "updateRouteDeviationNotification",
  "line": 342,
  "content": "    updateRouteDeviationNotification(route);",
  "context": [
    "    saved = routeRepository.save(route);",
    "    routeWialonService.updateUnits(saved);",
    "    updateRouteDeviationNotification(route);",
    "    notificationWialonService.updateGeozone(saved);",
    "    notificationWialonService.updateRoute(saved);"
  ],
  "match_count": 1
}
```

**Multiple Matches Output**:

```json
{
  "found": true,
  "file": "src/Service.java",
  "pattern": "save",
  "line": 156,
  "content": "    repository.save(entity);",
  "context": ["...", "...", "..."],
  "match_count": 3,
  "all_matches": [
    { "line": 156, "content": "    repository.save(entity);" },
    { "line": 298, "content": "    cache.save(data);" },
    { "line": 401, "content": "    file.save(path);" }
  ],
  "warning": "Multiple matches found (3). Using best match based on context."
}
```

**Exit Codes**:

- 0: Pattern found
- 1: Pattern not found or file error

**Examples**:

```bash
# Find exact line for method call
"$VCS_TOOL" find-line src/Service.java "updateRouteDeviationNotification"

# Find method definition
"$VCS_TOOL" find-line src/Service.java "createRouteUnits" --method

# Find with context hint to disambiguate
"$VCS_TOOL" find-line src/Service.java "save" "createRouteUnits"

# Use regex pattern
"$VCS_TOOL" find-line src/Service.java "save\(.*\)" --regex
```

**Why Use This Instead of grep?**

- ✅ Returns structured JSON output
- ✅ Provides surrounding context automatically
- ✅ Handles multiple matches intelligently
- ✅ Works with context hints to find the right match
- ✅ Specifically designed for code review workflows
- ✅ Exit codes for error handling

### 6. Format Review Comment (RECOMMENDED for Consistent Output)

**Script**: `format_review_comment.py`

**Purpose**: Generates consistently formatted code review and architecture review comments from structured JSON input. Ensures identical formatting every time, eliminating variations in manual template interpretation.

**Usage**:

```bash
"$VCS_TOOL" format-review <JSON_DATA>
```

**Parameters**:

- `JSON_DATA`: JSON string containing review data with `type` field ("code" or "architecture")

**Code Review Input JSON**:

```json
{
  "type": "code",
  "verdict": "PASS",
  "critical": [
    {
      "file": "src/Service.java",
      "line": 342,
      "url": "https://gitlab.com/.../Service.java#L342",
      "description": "Null pointer risk without validation"
    }
  ],
  "warnings": [
    {
      "file": "src/Controller.java",
      "line": 89,
      "url": "https://gitlab.com/.../Controller.java#L89",
      "description": "Missing error handling"
    }
  ],
  "suggestions": []
}
```

**Code Review Output**:

```markdown
# Code Review Summary 🔍

## 🔴 Critical Issues (Must Fix)

1. **src/Service.java** ([src/Service.java:342](https://gitlab.com/.../Service.java#L342)):
   Null pointer risk without validation

---

## 🟡 Warnings (Should Fix)

1. **src/Controller.java** ([src/Controller.java:89](https://gitlab.com/.../Controller.java#L89)):
   Missing error handling

---

## ✅ Verdict

**PASS** ✔️ - Ready for merge
```

**Architecture Review Input JSON**:

```json
{
  "type": "architecture",
  "strengths": [
    "Clear separation of concerns",
    "Repository pattern correctly applied"
  ],
  "concerns": [
    {
      "severity": "Critical",
      "description": "Direct database access in controller",
      "impact": "Tight coupling, difficult to test",
      "components": ["UserController", "DatabaseService"],
      "file": "src/controllers/UserController.java",
      "line": 45,
      "url": "https://gitlab.com/.../UserController.java#L45"
    }
  ],
  "recommendations": [
    {
      "priority": "High",
      "description": "Introduce service layer",
      "tradeoffs": "More abstraction but better testability",
      "effort": "Medium"
    }
  ],
  "compliance": [
    "Violates SRP in controller",
    "SOLID principles mostly followed"
  ]
}
```

**Architecture Review Output**:

```markdown
# Architecture Assessment 🏗️

## ✅ Strengths

- Clear separation of concerns
- Repository pattern correctly applied

---

## ⚠️ Architectural Concerns

1. 🔴 **Critical**: Direct database access in controller
   - **Impact**: Tight coupling, difficult to test
   - **Affected Components**: UserController, DatabaseService
   - **Location**: [src/controllers/UserController.java:45](https://gitlab.com/.../UserController.java#L45)

---

## 💡 Recommendations

1. 🔴 **High Priority**: Introduce service layer
   - **Trade-offs**: More abstraction but better testability
   - **Effort**: Medium

---

## 📋 Architecture Compliance

- Violates SRP in controller
- SOLID principles mostly followed
```

**Exit Codes**:

- 0: Successfully formatted
- 1: JSON parse error or invalid type

**Features**:

- ✅ **100% Consistent formatting** - identical output for same input
- ✅ **Automatic section skipping** - empty sections are omitted
- ✅ **Validated structure** - ensures required fields exist
- ✅ **Severity emojis** - visual indicators for priority (🔴🟠🟡🟢)
- ✅ **File links** - clickable links to exact code locations
- ✅ **Supports both review types** - code and architecture

**Why Use This?**

Without this script, Claude interprets markdown templates differently each time, leading to:

- ❌ Inconsistent formatting
- ❌ Missing sections
- ❌ Different emoji usage
- ❌ Varying link formats

With this script:

- ✅ Agents output structured JSON
- ✅ Script formats consistently
- ✅ Easy to update templates (change Python, not agent instructions)
- ✅ Guaranteed identical output

## Complete Workflow Examples

### Automatic Platform Detection (RECOMMENDED)

This is the recommended workflow that automatically detects whether you're working with GitHub or GitLab:

```bash
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

ISSUE_NUMBER="123"

PLATFORM=$("$VCS_TOOL" detect-platform)

if [ "$PLATFORM" = "gitlab" ]; then
    METADATA=$("$VCS_TOOL" get-gitlab-mr "$ISSUE_NUMBER")
elif [ "$PLATFORM" = "github" ]; then
    METADATA=$("$VCS_TOOL" get-github-pr "$ISSUE_NUMBER")
else
    echo "Error: Unsupported platform" >&2
    exit 1
fi

FILE_PATH="src/auth/login.ts"
LINE_NUMBER=42

URL_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"$PLATFORM\", file_path: \"$FILE_PATH\", line_number: $LINE_NUMBER}")

URL=$("$VCS_TOOL" format-url "$URL_INPUT")

"$VCS_TOOL" validate-url "$URL"
```

### Manual GitLab Merge Request Review

If you already know you're working with GitLab:

```bash
VCS_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/vcs-tool-manager/vcs-tool.sh

MR_NUMBER="123"

METADATA=$("$VCS_TOOL" get-gitlab-mr "$MR_NUMBER")

FILE_PATH="src/auth/login.ts"
LINE_NUMBER=42

URL_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"gitlab\", file_path: \"$FILE_PATH\", line_number: $LINE_NUMBER}")

URL=$("$VCS_TOOL" format-url "$URL_INPUT")

"$VCS_TOOL" validate-url "$URL"
```

### Manual GitHub Pull Request Review

If you already know you're working with GitHub:

```bash
VCS_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/vcs-tool-manager/vcs-tool.sh

PR_NUMBER="456"

METADATA=$("$VCS_TOOL" get-github-pr "$PR_NUMBER")

FILE_PATH="src/auth/login.ts"
LINE_NUMBER=42

URL_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"github\", file_path: \"$FILE_PATH\", line_number: $LINE_NUMBER}")

URL=$("$VCS_TOOL" format-url "$URL_INPUT")

"$VCS_TOOL" validate-url "$URL"
```

## Common Pitfalls to Avoid

### ❌ Not Detecting Platform First

Always use `detect_platform.py` before calling platform-specific scripts. Don't assume which VCS platform you're on.

### ❌ Using Branch Names in URLs (DEPRECATED)

The script previously allowed branch names in URLs, but this caused reliability issues:

- Branch names with `#` break URL anchors
- Branches can be deleted after merge
- Branches receive new commits, making line numbers incorrect

**Solution**: The script now **always uses commit SHA** for all generated URLs, ensuring permanent, reliable links.

### ❌ Guessing Branch from PR/MR Title

Never assume the source branch name from the MR/PR title. Always fetch metadata explicitly.

### ❌ Using Target Branch Instead of Source Branch

The target branch (usually `main` or `master`) doesn't contain the changes being reviewed. Always use the source branch or commit SHA.

### ✅ Always Use Commit SHA for Safety

When in doubt, use the commit SHA instead of branch name:

```
https://gitlab.com/org/repo/-/blob/abc123def456/path/file.ts#L10
```

## Integration with Code Review Workflows

This skill is designed to work seamlessly with the `code-reviewer` agent and `/code-review` command:

1. **Code Reviewer Agent** invokes this skill to generate file links
2. **Metadata Extraction** happens before analysis to ensure accurate references
3. **URL Validation** occurs before posting comments to MR/PR
4. **Line Numbers** are extracted from git diff output

## Prerequisites

- **GitLab**: `glab` CLI tool installed and authenticated
- **GitHub**: `gh` CLI tool installed and authenticated
- **Git**: Working git repository with configured remote
- **Python 3**: For running scripts
- **jq**: For JSON processing in bash workflows
- **curl**: For URL validation

## Error Handling

All scripts provide clear error messages and appropriate exit codes:

- **Exit 0**: Success
- **Exit 1**: Error (with message on stderr)

Example error output:

```
Error: Could not get git remote URL
Error: Could not parse GitLab URL from: invalid-url
Error: file_path is required
```

## Best Practices

1. **Always Detect Platform First**: Run `detect_platform.py` before calling platform-specific scripts to ensure you're using the correct tool
2. **Always Test Links**: Run `validate_url.py` before including links in comments
3. **Use Commit SHA for Complex Branches**: If branch has special chars, prefer SHA
4. **Verify Remote**: Ensure you're in correct git repository before running scripts
5. **Check CLI Tools**: Run `glab --version` or `gh --version` to verify installation
6. **Handle Errors Gracefully**: All scripts output JSON or structured text for parsing
7. **Self-Hosted GitLab**: No need to manually set `GITLAB_HOST` - scripts auto-detect from git remote

## Troubleshooting

**Issue**: "Error: Could not get git remote URL"

- **Solution**: Ensure you're in a git repository with configured remote

**Issue**: "404 Not Found" when fetching MR/PR metadata

- **Solution**: You may be using the wrong platform script (e.g., trying to fetch GitLab MR from a GitHub repository). Always run `detect_platform.py` first to identify the correct platform

**Issue**: "Error running glab mr view"

- **Solution**: Verify `glab` is installed and authenticated (`glab auth status`)

**Issue**: "Error running gh pr view"

- **Solution**: Verify `gh` is installed and authenticated (`gh auth status`)

**Issue**: "Invalid (HTTP 404)"

- **Solution**: Check if commit SHA exists on remote or branch was deleted

**Issue**: "URL anchor not working"

- **Solution**: Branch name likely contains `#` - use commit SHA instead
