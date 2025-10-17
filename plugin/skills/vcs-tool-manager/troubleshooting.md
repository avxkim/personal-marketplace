# VCS Tool Manager - Troubleshooting Guide

Common pitfalls, best practices, and solutions to errors.

## Common Pitfalls to Avoid

### ❌ Not Detecting Platform First

**Problem**: Calling `get-gitlab-mr` on a GitHub repository or vice versa.

**Why it fails**: The git remote URL won't match the expected platform format.

**Solution**: Always use `detect-platform` before calling platform-specific scripts.

```bash
# ❌ Wrong - assumes platform
METADATA=$("$VCS_TOOL" get-gitlab-mr "123")

# ✅ Correct - detects platform first
PLATFORM=$("$VCS_TOOL" detect-platform)
if [ "$PLATFORM" = "gitlab" ]; then
    METADATA=$("$VCS_TOOL" get-gitlab-mr "123")
else
    METADATA=$("$VCS_TOOL" get-github-pr "123")
fi
```

---

### ❌ Using Branch Names in URLs (DEPRECATED)

**Problem**: Using branch names creates unreliable URLs that break.

**Why it fails**:

- Branch names with `#` break URL anchors (e.g., `feature/task#123` → URL becomes `...task`)
- Branches can be deleted after merge → 404 errors
- Branches receive new commits → line numbers become incorrect

**Solution**: The script now **always uses commit SHA** for all generated URLs.

```bash
# ❌ Old behavior (no longer supported)
https://gitlab.com/org/repo/-/blob/feature/task#123/file.ts#L42

# ✅ Current behavior (automatic)
https://gitlab.com/org/repo/-/blob/abc123def456/file.ts#L42
```

**Note**: You don't need to do anything - the `format-url` command automatically uses SHA.

---

### ❌ Using Git Diff Line Numbers Directly

**Problem**: Git diff shows relative positions, not absolute file line numbers.

**Example of git diff output**:

```
@@ -258,5 +258,5 @@
```

This means "starting at line 258, showing 5 lines" - it's a **relative position**, not the actual line number of the change.

**Why it fails**: The actual change might be at line 260, 262, etc., but diff shows 258.

**Solution**: Always use the `find-line` command to get accurate absolute line numbers.

```bash
# ❌ Wrong - using git diff line number
LINE=258  # From @@ -258,5 +258,5 @@

# ✅ Correct - using find-line to get actual line
RESULT=$("$VCS_TOOL" find-line "src/Service.java" "methodName")
LINE=$(echo "$RESULT" | jq -r '.line')  # Returns actual line, e.g., 342
```

---

### ❌ Guessing Branch from PR/MR Title

**Problem**: Assuming the source branch name from the MR/PR title.

**Why it fails**: Titles and branch names often don't match, especially with task IDs and special conventions.

**Solution**: Always fetch metadata explicitly.

```bash
# ❌ Wrong - guessing branch
BRANCH="feature/add-authentication"  # Assumed from title

# ✅ Correct - fetching metadata
METADATA=$("$VCS_TOOL" get-gitlab-mr "123")
BRANCH=$(echo "$METADATA" | jq -r '.source_branch')  # Actual branch
```

---

### ❌ Using Target Branch Instead of Source Branch

**Problem**: Using the target branch (usually `main` or `dev`) instead of the source branch.

**Why it fails**: The target branch doesn't contain the changes being reviewed. Line numbers will be completely wrong or the code won't exist.

**Solution**: Always use `source_branch` (GitLab) or `head_ref` (GitHub) from metadata.

```bash
# ❌ Wrong - using target branch
BRANCH="main"  # Target branch

# ✅ Correct - using source branch
METADATA=$("$VCS_TOOL" get-gitlab-mr "123")
BRANCH=$(echo "$METADATA" | jq -r '.source_branch')  # Branch with changes
```

---

### ❌ Passing JSON as Command-Line Argument to format-review

**Problem**: Passing complex JSON with special characters as a command-line argument.

**Why it fails**: Shell escaping issues with quotes, backslashes, newlines, etc.

**Error example**:

```
Error parsing JSON: Invalid \escape: line 9 column 52 (char 563)
```

**Solution**: Always use heredoc with stdin (the `-` argument).

```bash
# ❌ Wrong - passing as argument
"$VCS_TOOL" format-review '{"type":"code",...}'

# ✅ Correct - using heredoc with stdin
cat <<'EOF' | "$VCS_TOOL" format-review -
{
  "type": "code",
  "verdict": "PASS",
  ...
}
EOF
```

---

## Best Practices

### 1. Always Detect Platform First

Run `detect-platform` before calling any platform-specific commands.

```bash
PLATFORM=$("$VCS_TOOL" detect-platform)
```

### 2. Always Use Commit SHA for URLs

Ensure generated URLs use commit SHA, not branch names. The `format-url` command does this automatically.

### 3. Always Use find-line for Line Numbers

Never rely on git diff positions or grep line numbers. Use the `find-line` command.

```bash
RESULT=$("$VCS_TOOL" find-line "$FILE" "$PATTERN")
LINE=$(echo "$RESULT" | jq -r '.line')
```

### 4. Always Validate URLs Before Posting

Test links via `validate-url` before including them in comments.

```bash
"$VCS_TOOL" validate-url "$URL"
if [ $? -eq 0 ]; then
    echo "URL is valid - safe to use"
fi
```

### 5. Always Use Heredoc for format-review

Avoid JSON escaping issues by using heredoc pattern.

```bash
cat <<'EOF' | "$VCS_TOOL" format-review -
{...}
EOF
```

### 6. Verify Git Repository Context

Ensure you're in the correct git repository before running scripts.

```bash
git remote -v  # Check which repository you're in
```

### 7. Handle Errors Gracefully

All scripts output to stderr for errors. Check exit codes and handle failures.

```bash
RESULT=$("$VCS_TOOL" find-line "$FILE" "$PATTERN")
if [ $? -ne 0 ]; then
    echo "Error: Pattern not found" >&2
    exit 1
fi
```

### 8. Self-Hosted GitLab

No need to manually set `GITLAB_HOST` - scripts auto-detect from git remote.

---

## Error Messages and Solutions

### Error: "Could not get git remote URL"

**Cause**: Not in a git repository or no remote configured.

**Solution**:

```bash
# Check if you're in a git repository
git status

# Check if remote is configured
git remote -v

# Add remote if missing
git remote add origin <URL>
```

---

### Error: "Could not parse GitLab/GitHub URL"

**Cause**: Git remote URL format is not recognized.

**Solution**: Ensure your remote URL follows standard format:

```
GitLab: https://gitlab.com/org/repo.git
        git@gitlab.com:org/repo.git

GitHub: https://github.com/owner/repo.git
        git@github.com:owner/repo.git
```

---

### Error: "404 Not Found" when fetching MR/PR metadata

**Cause**: Wrong platform script used (e.g., calling `get-gitlab-mr` on a GitHub repo).

**Solution**: Always run `detect-platform` first.

```bash
PLATFORM=$("$VCS_TOOL" detect-platform)
```

---

### Error: "Error running glab mr view"

**Cause**: `glab` CLI not installed or not authenticated.

**Solution**:

```bash
# Check if glab is installed
glab --version

# Install if missing (macOS)
brew install glab

# Authenticate
glab auth login

# Verify authentication
glab auth status
```

---

### Error: "Error running gh pr view"

**Cause**: `gh` CLI not installed or not authenticated.

**Solution**:

```bash
# Check if gh is installed
gh --version

# Install if missing (macOS)
brew install gh

# Authenticate
gh auth login

# Verify authentication
gh auth status
```

---

### Error: "Invalid (HTTP 404)" from validate-url

**Cause**:

1. Commit SHA doesn't exist on remote
2. Branch was deleted
3. File path is incorrect
4. Private repository without authentication

**Solution**:

```bash
# Verify commit exists on remote
git log --oneline | grep <SHA>

# Verify file exists
ls -la <file_path>

# For private repos, ensure CLI tools are authenticated
glab auth status  # GitLab
gh auth status    # GitHub
```

---

### Error: "URL anchor not working" (line number not highlighting)

**Cause**: Branch name contains `#` character, breaking the URL anchor.

**Example**: `feature/task#123` in URL becomes `...task` (everything after `#` is anchor)

**Solution**: This is automatically fixed - the script always uses commit SHA now, not branch names.

---

### Error: "Pattern not found in file" from find-line

**Cause**:

1. Pattern doesn't exist in the file
2. Pattern syntax is incorrect
3. Wrong file path

**Solution**:

```bash
# Check if file exists
ls -la <file_path>

# Try reading the file to see content
cat <file_path> | grep -n <pattern>

# Use simpler pattern
"$VCS_TOOL" find-line "$FILE" "simpler"

# Check JSON output for details
RESULT=$("$VCS_TOOL" find-line "$FILE" "$PATTERN")
echo "$RESULT" | jq '.'
```

---

### Error: "Multiple matches found" warning from find-line

**Cause**: Pattern appears multiple times in the file.

**Solution**: Use context hint to disambiguate.

```bash
# Without hint - returns first match with warning
"$VCS_TOOL" find-line "src/Service.java" "save"

# With hint - finds save() within specific method
"$VCS_TOOL" find-line "src/Service.java" "save" "processOrder"
```

---

### Error: "Error parsing JSON: Invalid \escape"

**Cause**: Passing JSON with special characters as command-line argument to `format-review`.

**Solution**: Use heredoc with stdin.

```bash
# ❌ Causes escaping errors
"$VCS_TOOL" format-review '{"description":"Fix \"issue\""}'

# ✅ No escaping issues
cat <<'EOF' | "$VCS_TOOL" format-review -
{"description":"Fix \"issue\""}
EOF
```

---

## Debugging Tips

### Enable Debug Output

Add `-x` to bash commands to see exactly what's being executed:

```bash
bash -x "$VCS_TOOL" detect-platform
```

### Check Script Permissions

Ensure scripts are executable:

```bash
ls -la ~/.claude/plugins/*/plugin/skills/vcs-tool-manager/vcs-tool.sh
chmod +x ~/.claude/plugins/*/plugin/skills/vcs-tool-manager/vcs-tool.sh
```

### Verify jq Installation

Many scripts rely on `jq` for JSON processing:

```bash
jq --version

# Install if missing (macOS)
brew install jq
```

### Check Python Version

Scripts require Python 3:

```bash
python3 --version

# Should be 3.7 or higher
```

---

## Getting Help

If you encounter issues not covered here:

1. **Check prerequisites**: Ensure all required tools are installed
2. **Verify authentication**: Run `glab auth status` or `gh auth status`
3. **Check git context**: Ensure you're in correct repository
4. **Enable debug mode**: Use `bash -x` to see command execution
5. **Read error messages**: Scripts provide detailed error output on stderr
