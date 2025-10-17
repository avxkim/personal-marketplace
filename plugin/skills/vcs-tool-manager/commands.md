# VCS Tool Manager - Command Reference

Detailed documentation for all vcs-tool commands.

## Command: detect-platform

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

**Note**: Always run this command first before calling platform-specific metadata scripts.

---

## Command: get-gitlab-mr

**Purpose**: Extracts metadata from a GitLab merge request including source branch, commit SHA, and repository details.

**Usage**:

```bash
"$VCS_TOOL" get-gitlab-mr <MR_NUMBER>
```

**Parameters**:

- `MR_NUMBER`: GitLab merge request number (e.g., 123)

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

**JSON Fields**:

- `host`: GitLab host (gitlab.com or self-hosted domain)
- `namespace`: Organization or user namespace
- `repo`: Repository name
- `source_branch`: Source branch name (contains the changes)
- `sha`: HEAD commit SHA of the source branch
- `web_url`: Full URL to the merge request

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

**Exit Codes**:

- 0: Metadata retrieved successfully
- 1: Error (git remote not found, glab command failed, or MR not found)

**Error Messages**:

```
Error: Could not get git remote URL
Error: Could not parse GitLab URL from: <url>
Error: Could not fetch MR metadata
```

---

## Command: get-github-pr

**Purpose**: Extracts metadata from a GitHub pull request including head branch, commit SHA, and repository details.

**Usage**:

```bash
"$VCS_TOOL" get-github-pr <PR_NUMBER>
```

**Parameters**:

- `PR_NUMBER`: GitHub pull request number (e.g., 456)

**Output** (JSON):

```json
{
  "owner": "myorg",
  "repo": "myrepo",
  "head_ref": "feature/add-authentication",
  "sha": "abc123def456",
  "web_url": "https://github.com/myorg/myrepo/pull/456"
}
```

**JSON Fields**:

- `owner`: GitHub organization or user
- `repo`: Repository name
- `head_ref`: Head branch name (contains the changes)
- `sha`: HEAD commit SHA of the head branch
- `web_url`: Full URL to the pull request

**How It Works**:

1. Retrieves git remote URL from current repository
2. Parses GitHub owner and repo name
3. Fetches PR metadata using `gh pr view` command with JSON output

**Exit Codes**:

- 0: Metadata retrieved successfully
- 1: Error (git remote not found, gh command failed, or PR not found)

**Error Messages**:

```
Error: Could not get git remote URL
Error: Could not parse GitHub URL from: <url>
Error: Could not fetch PR metadata
```

---

## Command: format-url

**Purpose**: Generates properly formatted blob URLs with line numbers for both GitLab and GitHub.

**Usage**:

```bash
"$VCS_TOOL" format-url '<JSON_METADATA>'
```

**Parameters**:

- `JSON_METADATA`: JSON string containing platform, repository info, file path, and line number

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

**Required Fields**:

- `platform`: "gitlab" or "github"
- `file_path`: Relative path to file from repository root
- `line_number`: Line number to reference
- `sha`: Commit SHA

**GitLab-Specific Required Fields**:

- `host`: GitLab host (e.g., "gitlab.com" or "gitlab.mycompany.com")
- `namespace`: Organization/user namespace
- `repo`: Repository name

**GitHub-Specific Required Fields**:

- `owner`: GitHub owner (org or user)
- `repo`: Repository name

**Output Examples**:

GitLab:

```
https://gitlab.example.com/myorg/myrepo/-/blob/abc123def456/src/auth/login.ts#L42
```

GitHub:

```
https://github.com/myorg/myrepo/blob/abc123def456/src/auth/login.ts#L42
```

**URL Generation Rules**:

- **Always uses commit SHA** for reliable, permanent links that won't break after branch deletion or updates
- URL-encodes file paths properly (spaces, special characters)
- Appends `#L{line_number}` for line anchors

**Exit Codes**:

- 0: URL generated successfully
- 1: Error (missing required fields or invalid platform)

**Error Messages**:

```
Error: file_path is required
Error: line_number is required
Error: platform must be 'gitlab' or 'github'
Error: Missing required field: <field_name>
```

---

## Command: validate-url

**Purpose**: Tests URLs via curl to ensure they return valid HTTP status codes (200 or 302).

**Usage**:

```bash
"$VCS_TOOL" validate-url <URL>
```

**Parameters**:

- `URL`: Full URL to validate

**Output**:

```
URL: https://gitlab.example.com/myorg/myrepo/-/blob/abc123/file.ts#L42
Status: Valid
HTTP Code: 200
```

or

```
URL: https://gitlab.example.com/myorg/myrepo/-/blob/invalid/file.ts
Status: Invalid
HTTP Code: 404
```

**Valid HTTP Codes**:

- 200: OK
- 302: Redirect (common for authentication flows)

**Exit Codes**:

- 0: URL is valid (HTTP 200 or 302)
- 1: URL is invalid or unreachable

**How It Works**:

1. Uses `curl -s -o /dev/null -w "%{http_code}"` to fetch HTTP status
2. Checks if status is 200 or 302
3. Outputs result and returns appropriate exit code

---

## Command: find-line

**Purpose**: Finds accurate line numbers in source files for code patterns. This solves the problem of git diff showing relative positions instead of absolute file line numbers.

**Usage**:

```bash
"$VCS_TOOL" find-line <file_path> <pattern> [context_hint] [--method|--regex]
```

**Parameters**:

- `file_path`: Absolute or relative path to the source file
- `pattern`: Code snippet or pattern to search for
- `context_hint` (optional): Additional context to disambiguate multiple matches
- `--method` (optional): Search for method/function definitions
- `--regex` (optional): Use regex pattern matching instead of literal string

**Output** (JSON):

**Single Match:**

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

**Multiple Matches:**

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

**Not Found:**

```json
{
  "found": false,
  "file": "src/Service.java",
  "pattern": "nonexistent",
  "error": "Pattern not found in file"
}
```

**JSON Fields**:

- `found`: Boolean indicating if pattern was found
- `file`: File path that was searched
- `pattern`: Search pattern used
- `line`: Line number where pattern was found (1-indexed)
- `content`: Exact line content
- `context`: Array of surrounding lines (2 before + match + 2 after)
- `match_count`: Total number of matches found
- `all_matches`: Array of all matches when multiple found
- `warning`: Message when multiple matches exist
- `error`: Error message when pattern not found

**Search Types**:

1. **Literal String (default)**: Exact substring match
2. **Method Search (`--method`)**: Finds method/function definitions
3. **Regex (`--regex`)**: Uses Python regex patterns

**Context Disambiguation**:

When multiple matches exist, you can provide a `context_hint` to find the right one:

```bash
# Without hint - might return wrong match
"$VCS_TOOL" find-line src/Service.java "save"

# With hint - finds save() call within createRouteUnits method
"$VCS_TOOL" find-line src/Service.java "save" "createRouteUnits"
```

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
- ✅ 1-based line indexing (matches editor line numbers)

**Exit Codes**:

- 0: Pattern found
- 1: Pattern not found or file error

---

## Command: format-review

**Purpose**: Generates consistently formatted code review and architecture review comments from structured JSON input. Ensures identical formatting every time.

**Usage**:

```bash
# Method 1: Using heredoc (RECOMMENDED - best for complex JSON)
cat <<'EOF' | "$VCS_TOOL" format-review -
{JSON_DATA}
EOF

# Method 2: Using echo with stdin
echo '<JSON_DATA>' | "$VCS_TOOL" format-review -

# Method 3: Pass as argument (only for simple JSON without special chars)
"$VCS_TOOL" format-review '<JSON_DATA>'
```

**Parameters**:

- `JSON_DATA`: JSON string containing review data with `type` field
- `-`: Read from stdin (recommended to avoid escaping issues)

**Input Types**:

1. **Code Review** (`"type": "code"`)
2. **Architecture Review** (`"type": "architecture"`)

### Code Review Format

**Input JSON**:

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
      "description": "Missing error handling"
    }
  ],
  "suggestions": []
}
```

**Required Fields**:

- `type`: "code"
- `verdict`: "PASS" or "FAIL"
- `critical`: Array of critical issues (blocks approval)
- `warnings`: Array of warnings (should fix)
- `suggestions`: Array of suggestions (consider)

**Issue Fields**:

- `file`: File path (required)
- `description`: Issue description with backticks for code references (required)
- `line`: Line number (optional, but recommended)
- `url`: Clickable link to code location (optional, but recommended)

**Output Markdown**:

```markdown
# Code Review Summary 🔍

## 🔴 Critical Issues (Must Fix)

1. <big>**Service.java**</big> ([src/Service.java:342](https://gitlab.com/.../Service.java#L342)):
   Null pointer risk without validation

---

## 🟡 Warnings (Should Fix)

1. <big>**Controller.java**</big> (src/Controller.java):
   Missing error handling

---

## ⚖️ Verdict

**PASS** ✔️ - Ready for merge
```

### Architecture Review Format

**Input JSON**:

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
      "description": "Direct database access in `UserController` violates separation of concerns",
      "file": "src/controllers/UserController.java",
      "line": 45,
      "url": "https://gitlab.com/.../UserController.java#L45"
    }
  ],
  "compliance": [
    "Violates SRP in controller",
    "SOLID principles mostly followed"
  ]
}
```

**Required Fields**:

- `type`: "architecture"
- `strengths`: Array of positive architectural decisions
- `concerns`: Array of architectural issues
- `compliance`: Array of SOLID/DRY/KISS/YAGNI observations

**Concern Fields**:

- `severity`: "Critical", "Major", or "Minor" (required)
- `description`: Issue description with backticks for code references (required)
- `file`: File path (optional)
- `line`: Line number (optional)
- `url`: Clickable link to code location (optional)

**Output Markdown**:

```markdown
# Architecture Assessment 🏗️

## ✅ Strengths

- Clear separation of concerns
- Repository pattern correctly applied

---

## ⚠️ Architectural Concerns

1. 🔴 <big>**UserController.java**</big> ([src/controllers/UserController.java:45](https://...)): Direct database access in `UserController` violates separation of concerns

---

## 📋 Architecture Compliance

- Violates SRP in controller
- SOLID principles mostly followed
```

**Features**:

- ✅ **100% Consistent formatting** - identical output for same input
- ✅ **Automatic section skipping** - empty sections are omitted
- ✅ **Validated structure** - ensures required fields exist
- ✅ **Severity emojis** - visual indicators (🔴🟠🟡🟢⚖️)
- ✅ **File links** - clickable links to exact code locations
- ✅ **Filename emphasis** - Uses `<big>` HTML tags for visibility
- ✅ **Supports both review types** - code and architecture

**Why Use stdin (heredoc)?**

Passing JSON as command-line argument causes issues with:

- ❌ Special characters (quotes, backslashes, newlines)
- ❌ Shell escaping problems
- ❌ Size limitations
- ❌ Complex nested structures

Using stdin with heredoc:

- ✅ No escaping issues
- ✅ Handles special characters correctly
- ✅ No size limits
- ✅ Readable and maintainable

**Exit Codes**:

- 0: Successfully formatted
- 1: JSON parse error or invalid type

**Error Messages**:

```
Error parsing JSON: <details>
Error: Invalid type '<type>'. Use 'code' or 'architecture'
```

---

## Command: post-comment

**Purpose**: Posts a comment to a GitLab merge request or GitHub pull request using the appropriate CLI tool.

**Usage**:

```bash
# Method 1: Pass comment directly
"$VCS_TOOL" post-comment <platform> <issue_number> "Comment text"

# Method 2: Use stdin (recommended for long/multiline comments)
cat <<'EOF' | "$VCS_TOOL" post-comment <platform> <issue_number> -
Comment text here
EOF

# Method 3: Pipe from variable
echo "$COMMENT" | "$VCS_TOOL" post-comment <platform> <issue_number> -
```

**Parameters**:

- `platform`: "gitlab" or "github" (required)
- `issue_number`: MR/PR number as string (required)
- `comment`: Comment text (required)
  - Pass directly as argument for short comments
  - Use `-` to read from stdin for long/multiline comments

**Examples**:

```bash
# GitLab MR - simple comment
"$VCS_TOOL" post-comment gitlab 123 "LGTM! Ready to merge."

# GitHub PR - long formatted comment
cat <<'EOF' | "$VCS_TOOL" post-comment github 456 -
# Code Review Summary 🔍

## 🔴 Critical Issues (Must Fix)

1. **Service.java** ([src/Service.java:342](...)): Null pointer risk

## ⚖️ Verdict

**FAIL** ❌ - Requires fixes before merge
EOF

# Using variable with formatted review
FINAL_COMMENT="$CODE_REVIEW

---

$ARCH_REVIEW"

echo "$FINAL_COMMENT" | "$VCS_TOOL" post-comment gitlab 175 -
```

**How It Works**:

1. Validates platform is "gitlab" or "github"
2. Validates issue number is provided
3. Reads comment text (from argument or stdin)
4. Calls appropriate CLI tool:
   - GitLab: `glab mr note <MR_NUMBER> -m <comment>`
   - GitHub: `gh pr comment <PR_NUMBER> --body <comment>`
5. Returns success/error message

**Output**:

Success:

```
✅ Comment posted successfully to GitLab #123
```

Error:

```
Error posting to GitLab MR: <error details>
Error: glab CLI not found. Install with: brew install glab
```

**Exit Codes**:

- 0: Comment posted successfully
- 1: Error (invalid parameters, CLI tool error, or network error)

**Error Messages**:

```
Error: Invalid platform 'foo'. Use 'gitlab' or 'github'
Error: Comment cannot be empty
Error: glab CLI not found. Install with: brew install glab
Error: gh CLI not found. Install with: brew install gh
Error posting to GitLab MR: <glab error>
Error posting to GitHub PR: <gh error>
```

**Prerequisites**:

- GitLab: `glab` CLI installed and authenticated (`glab auth login`)
- GitHub: `gh` CLI installed and authenticated (`gh auth login`)

**Why Use This Instead of glab/gh Directly?**

- ✅ Unified interface for both platforms
- ✅ Consistent error handling
- ✅ Proper stdin support for long comments
- ✅ Clear success/failure messages
- ✅ Exit codes for error handling
- ✅ Centralized with other VCS operations
