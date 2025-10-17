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

## Available Scripts

All scripts are located in the `scripts/` directory and can be invoked via Bash.

### 0. Detect Platform (REQUIRED FIRST STEP)

**Script**: `detect_platform.py`

**Purpose**: Automatically detects whether the current repository is on GitHub or GitLab by analyzing the git remote URL.

**Usage**:

```bash
PLATFORM=$(python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/detect_platform.py)
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
python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/get_gitlab_mr_metadata.py <MR_NUMBER>
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
python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/get_github_pr_metadata.py <PR_NUMBER>
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
python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/format_blob_url.py '<JSON_METADATA>'
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

**Special Character Handling**:

- Automatically uses commit SHA instead of branch name if branch contains `#`, `%`, or spaces
- URL-encodes file paths properly

### 4. Validate URL

**Script**: `validate_url.py`

**Purpose**: Tests URLs via curl to ensure they return valid HTTP status codes (200 or 302).

**Usage**:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/validate_url.py <URL>
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

## Complete Workflow Examples

### Automatic Platform Detection (RECOMMENDED)

This is the recommended workflow that automatically detects whether you're working with GitHub or GitLab:

```bash
ISSUE_NUMBER="123"

PLATFORM=$(python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/detect_platform.py)

if [ "$PLATFORM" = "gitlab" ]; then
    METADATA=$(python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/get_gitlab_mr_metadata.py "$ISSUE_NUMBER")
elif [ "$PLATFORM" = "github" ]; then
    METADATA=$(python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/get_github_pr_metadata.py "$ISSUE_NUMBER")
else
    echo "Error: Unsupported platform" >&2
    exit 1
fi

FILE_PATH="src/auth/login.ts"
LINE_NUMBER=42

URL_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"$PLATFORM\", file_path: \"$FILE_PATH\", line_number: $LINE_NUMBER}")

URL=$(python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/format_blob_url.py "$URL_INPUT")

python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/validate_url.py "$URL"
```

### Manual GitLab Merge Request Review

If you already know you're working with GitLab:

```bash
MR_NUMBER="123"

METADATA=$(python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/get_gitlab_mr_metadata.py "$MR_NUMBER")

FILE_PATH="src/auth/login.ts"
LINE_NUMBER=42

URL_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"gitlab\", file_path: \"$FILE_PATH\", line_number: $LINE_NUMBER}")

URL=$(python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/format_blob_url.py "$URL_INPUT")

python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/validate_url.py "$URL"
```

### Manual GitHub Pull Request Review

If you already know you're working with GitHub:

```bash
PR_NUMBER="456"

METADATA=$(python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/get_github_pr_metadata.py "$PR_NUMBER")

FILE_PATH="src/auth/login.ts"
LINE_NUMBER=42

URL_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"github\", file_path: \"$FILE_PATH\", line_number: $LINE_NUMBER}")

URL=$(python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/format_blob_url.py "$URL_INPUT")

python3 ${CLAUDE_PLUGIN_ROOT}/plugin/skills/vcs-tool-manager/scripts/validate_url.py "$URL"
```

## Common Pitfalls to Avoid

### ❌ Not Detecting Platform First

Always use `detect_platform.py` before calling platform-specific scripts. Don't assume which VCS platform you're on.

### ❌ Using Branch Names with Special Characters

```
https://gitlab.com/org/repo/-/blob/feature/TASK-123/path/file.ts#L10
```

The `#` in branch names breaks URL anchors. Solution: Use commit SHA.

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
