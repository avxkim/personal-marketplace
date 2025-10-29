# VCS Tool Manager - Workflow Examples

Complete end-to-end examples for common code review scenarios.

## Example 1: Automatic Platform Detection (Recommended)

This workflow automatically detects whether you're working with GitHub or GitLab and adapts accordingly.

```bash
# Step 1: Locate the VCS tool
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

# Step 2: Detect platform
PLATFORM=$("$VCS_TOOL" detect-platform)
echo "Detected platform: $PLATFORM"

# Step 3: Get MR/PR metadata (auto-selects correct command)
ISSUE_NUMBER="123"
if [ "$PLATFORM" = "gitlab" ]; then
    METADATA=$("$VCS_TOOL" get-gitlab-mr "$ISSUE_NUMBER")
elif [ "$PLATFORM" = "github" ]; then
    METADATA=$("$VCS_TOOL" get-github-pr "$ISSUE_NUMBER")
else
    echo "Error: Unsupported platform" >&2
    exit 1
fi

# Step 4: Extract values from metadata
SHA=$(echo "$METADATA" | jq -r '.sha')
echo "Commit SHA: $SHA"

# Step 5: Find accurate line number for code issue
FILE_PATH="src/controllers/UserController.java"
RESULT=$("$VCS_TOOL" find-line "$FILE_PATH" "directDatabaseAccess")
LINE=$(echo "$RESULT" | jq -r '.line')
CONTENT=$(echo "$RESULT" | jq -r '.content')
echo "Found at line $LINE: $CONTENT"

# Step 6: Generate URL
URL_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"$PLATFORM\", file_path: \"$FILE_PATH\", line_number: $LINE}")
URL=$("$VCS_TOOL" format-url "$URL_INPUT")
echo "Generated URL: $URL"

# Step 7: Validate URL before using
"$VCS_TOOL" validate-url "$URL"
```

**Output:**

```
Detected platform: gitlab
Commit SHA: abc123def456
Found at line 45: public void updateUser() { database.execute(...); }
Generated URL: https://gitlab.com/org/repo/-/blob/abc123def456/src/controllers/UserController.java#L45
URL: https://gitlab.com/org/repo/-/blob/abc123def456/src/controllers/UserController.java#L45
Status: Valid
HTTP Code: 200
```

---

## Example 2: GitLab Code Review with Multiple Issues

This example shows how to generate multiple file links for a GitLab merge request review.

```bash
# Locate tool
VCS_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/vcs-tool-manager/vcs-tool.sh

# Get MR metadata
MR_NUMBER="175"
METADATA=$("$VCS_TOOL" get-gitlab-mr "$MR_NUMBER")

# Extract base info
PLATFORM="gitlab"

# Issue 1: Missing null check
FILE1="src/controllers/ShiftController.java"
RESULT1=$("$VCS_TOOL" find-line "$FILE1" "endByAdmin" --method)
LINE1=$(echo "$RESULT1" | jq -r '.line')
URL1_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"$PLATFORM\", file_path: \"$FILE1\", line_number: $LINE1}")
URL1=$("$VCS_TOOL" format-url "$URL1_INPUT")

# Issue 2: Missing authorization check
FILE2="src/config/SecurityConfig.java"
RESULT2=$("$VCS_TOOL" find-line "$FILE2" "@PreAuthorize")
LINE2=$(echo "$RESULT2" | jq -r '.line')
URL2_INPUT=$(echo "$METADATA" | jq -c ". + {platform: \"$PLATFORM\", file_path: \"$FILE2\", line_number: $LINE2}")
URL2=$("$VCS_TOOL" format-url "$URL2_INPUT")

# Build code review JSON
CODE_REVIEW_JSON=$(cat <<'EOF'
{
  "type": "code",
  "verdict": "FAIL",
  "critical": [
    {
      "file": "src/controllers/ShiftController.java",
      "line": 160,
      "url": "https://gitlab.com/org/repo/-/blob/abc123/ShiftController.java#L160",
      "description": "Incorrect audit tracking - uses `@shiftService.getById(#request.driverId)` which fetches by driver ID instead of shift ID"
    },
    {
      "file": "src/config/SecurityConfig.java",
      "line": 89,
      "url": "https://gitlab.com/org/repo/-/blob/abc123/SecurityConfig.java#L89",
      "description": "Missing fleet-scoped authorization with `@PreAuthorize` - any admin can manipulate shifts across all fleets"
    }
  ],
  "warnings": [],
  "suggestions": []
}
EOF
)

# Format review comment
FORMATTED_REVIEW=$(echo "$CODE_REVIEW_JSON" | "$VCS_TOOL" format-review -)

# Display formatted output
echo "$FORMATTED_REVIEW"
```

---

## Example 3: GitHub Pull Request Architecture Review

This example shows how to review architecture concerns for a GitHub pull request.

```bash
# Locate tool
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

# Get PR metadata
PR_NUMBER="456"
METADATA=$("$VCS_TOOL" get-github-pr "$PR_NUMBER")

# Build architecture review
ARCH_REVIEW=$(cat <<'EOF' | "$VCS_TOOL" format-review -
{
  "type": "architecture",
  "strengths": [
    "Clear separation of concerns between controller and service layers",
    "Repository pattern correctly applied for data access"
  ],
  "concerns": [
    {
      "severity": "Critical",
      "description": "Missing fleet-scoped authorization - `SecurityConfig` grants broad `SYS_ADMIN` access without tenant isolation checks. Recommendation: Implement `@PreAuthorize` with custom permission evaluator validating admin has authority over target driver's fleet (Effort: 2-3 SP)",
      "file": "src/config/SecurityConfig.java",
      "line": 45,
      "url": "https://github.com/org/repo/blob/abc123/src/config/SecurityConfig.java#L45"
    },
    {
      "severity": "Critical",
      "description": "No external service synchronization for admin shift lifecycle events - billing service won't detect admin-started shifts for revenue calculations; notification service won't alert affected parties; Wialon integration may show phantom trips",
      "file": "src/services/ShiftService.java",
      "line": 120,
      "url": "https://github.com/org/repo/blob/abc123/src/services/ShiftService.java#L120"
    }
  ],
  "compliance": [
    "Violates single responsibility - controller handles both HTTP and business logic",
    "SOLID principles mostly followed except for SRP violation"
  ]
}
EOF
)

# Display formatted output
echo "$ARCH_REVIEW"
```

**Output:**

```markdown
# Architecture Assessment 🏗️

## 🔴 Critical Concerns (Must Address)

1. <big>**SecurityConfig.java**</big> ([src/config/SecurityConfig.java:45](https://...)):
   Missing fleet-scoped authorization - `SecurityConfig` grants broad `SYS_ADMIN` access without tenant isolation checks. Recommendation: Implement `@PreAuthorize` with custom permission evaluator validating admin has authority over target driver's fleet (Effort: 2-3 SP)

2. <big>**ShiftService.java**</big> ([src/services/ShiftService.java:120](https://...)):
   No external service synchronization for admin shift lifecycle events - billing service won't detect admin-started shifts for revenue calculations; notification service won't alert affected parties; Wialon integration may show phantom trips

---

## 🟠 Major Concerns (Should Address)

1. <big>**UserController.java**</big> ([src/controllers/UserController.java:89](https://...)):
   Violates single responsibility - controller handles both HTTP and business logic

---
```

---

## Example 4: Combining Code and Architecture Reviews

This example shows the complete workflow used by the `/code-review` command.

```bash
# Locate tool
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

# Detect platform and get metadata
PLATFORM=$("$VCS_TOOL" detect-platform)
ISSUE_NUMBER="123"

if [ "$PLATFORM" = "gitlab" ]; then
    METADATA=$("$VCS_TOOL" get-gitlab-mr "$ISSUE_NUMBER")
else
    METADATA=$("$VCS_TOOL" get-github-pr "$ISSUE_NUMBER")
fi

# In real usage, you would get JSON from agent output:
# CODE_REVIEW_JSON=$(agent output...)
# But for this example, we'll use heredoc to show the JSON structure:

# Format code review (from code-reviewer agent output)
# NOTE: Use heredoc for literal JSON in examples, use printf with variables in real code
CODE_COMMENT=$(cat <<'EOF_CODE' | "$VCS_TOOL" format-review -
{
  "type": "code",
  "verdict": "FAIL",
  "critical": [
    {
      "file": "src/Service.java",
      "line": 342,
      "url": "https://gitlab.com/.../Service.java#L342",
      "description": "Null pointer risk in `processRequest()` without validation"
    }
  ],
  "warnings": [
    {
      "file": "src/Controller.java",
      "line": 89,
      "description": "Missing error handling for `validateInput()`"
    }
  ],
  "suggestions": []
}
EOF_CODE
)

# Format architecture review (from software-architect agent output)
# NOTE: Use heredoc for literal JSON in examples, use printf with variables in real code
ARCH_COMMENT=$(cat <<'EOF_ARCH' | "$VCS_TOOL" format-review -
{
  "type": "architecture",
  "concerns": [
    {
      "severity": "Major",
      "description": "Direct database access in `Controller` layer bypasses service abstraction",
      "file": "src/Controller.java",
      "line": 156,
      "url": "https://gitlab.com/.../Controller.java#L156"
    }
  ]
}
EOF_ARCH
)

# ALTERNATIVE: If you have JSON in variables (real agent output scenario):
# CODE_COMMENT=$(printf '%s' "$CODE_REVIEW_JSON" | "$VCS_TOOL" format-review -)
# ARCH_COMMENT=$(printf '%s' "$ARCH_REVIEW_JSON" | "$VCS_TOOL" format-review -)

# Combine both reviews
FINAL_COMMENT="$CODE_COMMENT

---

$ARCH_COMMENT"

# Display final combined review
echo "$FINAL_COMMENT"

# Ask user before posting
echo ""
echo "Post this review to MR/PR #$ISSUE_NUMBER? [y/N]"
read -r CONFIRM

if [ "$CONFIRM" = "y" ]; then
    if [ "$PLATFORM" = "gitlab" ]; then
        glab mr note "$ISSUE_NUMBER" -m "$FINAL_COMMENT"
    else
        gh pr comment "$ISSUE_NUMBER" --body "$FINAL_COMMENT"
    fi
    echo "Review posted successfully!"
fi
```

---

## Example 5: Finding Multiple Occurrences with Context

This example shows how to use context hints when a pattern appears multiple times in a file.

```bash
VCS_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/vcs-tool-manager/vcs-tool.sh

FILE="src/services/DataService.java"

# First, search without context - finds multiple matches
RESULT1=$("$VCS_TOOL" find-line "$FILE" "save")
echo "Matches found: $(echo "$RESULT1" | jq -r '.match_count')"
echo "All matches:"
echo "$RESULT1" | jq '.all_matches'

# Now search with context hint to find the specific save() call
RESULT2=$("$VCS_TOOL" find-line "$FILE" "save" "processOrder")
LINE=$(echo "$RESULT2" | jq -r '.line')
CONTENT=$(echo "$RESULT2" | jq -r '.content')

echo ""
echo "Specific match in processOrder method:"
echo "Line $LINE: $CONTENT"
```

**Output:**

```
Matches found: 3
All matches:
[
  { "line": 156, "content": "    repository.save(entity);" },
  { "line": 298, "content": "    cache.save(data);" },
  { "line": 401, "content": "    file.save(path);" }
]

Specific match in processOrder method:
Line 156:     repository.save(entity);
```

---

## Example 6: Method Definition Search

This example shows how to search for method definitions specifically.

```bash
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

FILE="src/controllers/UserController.java"

# Find the method definition (not method calls)
RESULT=$("$VCS_TOOL" find-line "$FILE" "updateUser" --method)

if [ "$(echo "$RESULT" | jq -r '.found')" = "true" ]; then
    LINE=$(echo "$RESULT" | jq -r '.line')
    CONTENT=$(echo "$RESULT" | jq -r '.content')

    echo "Method definition found:"
    echo "Line $LINE: $CONTENT"

    echo ""
    echo "Context:"
    echo "$RESULT" | jq -r '.context[]'
else
    echo "Method definition not found"
fi
```

**Output:**

```
Method definition found:
Line 89: public ResponseEntity<User> updateUser(@RequestBody UserDto dto) {

Context:
    }

    public ResponseEntity<User> updateUser(@RequestBody UserDto dto) {
        User user = userService.update(dto);
        return ResponseEntity.ok(user);
```

---

## Integration with Code Review Agents

The vcs-tool-manager skill is automatically invoked by code review agents. Here's how it fits into the workflow:

```
User runs: /code-review https://gitlab.com/org/repo/-/merge_requests/123

1. code-review command detects platform → invokes vcs-tool detect-platform
2. code-review command fetches MR metadata → invokes vcs-tool get-gitlab-mr
3. code-reviewer agent runs → analyzes code changes
4. code-reviewer agent needs line number → invokes vcs-tool find-line
5. code-reviewer agent generates URL → invokes vcs-tool format-url
6. code-reviewer agent validates link → invokes vcs-tool validate-url
7. code-reviewer agent returns JSON → vcs-tool format-review formats it
8. software-architect agent runs in parallel → same workflow
9. Both formatted reviews combined
10. User confirms → review posted to MR via glab
```

This ensures:

- ✅ Accurate line numbers (not git diff positions)
- ✅ Permanent links using commit SHA
- ✅ Validated URLs before posting
- ✅ Consistent markdown formatting
