## Code review guidance

- MR/PR url: $ARGUMENTS
- **Working Directory**: Agents will check current directory first and only clone if necessary
- ALWAYS delegate review to `code-reviewer` agent with the MR/PR URL from $ARGUMENTS
- **CRITICAL**: Include "OUTPUT_FORMAT=JSON" in agent delegation prompts (agents check for this to output JSON vs markdown)
- The `code-reviewer` agent will use the `avx:vcs-tool-manager` skill's `find-line` command to get accurate line numbers and generate validated links
- **Line Number Resolution**: Uses Python-based `find-line` tool (NOT git diff positions) to ensure links point to correct code
- The code-reviewer agent will provide PASS/FAIL verdict, `software-architect` agent should run in parallel with `code-reviewer`

## Before Delegating to Agents:

**1. Detect Platform**

```bash
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)
PLATFORM=$("$VCS_TOOL" detect-platform)
```

**2. Fetch MR/PR Details and Existing Comments**

Extract MR/PR number from $ARGUMENTS (URL or number)

**IMPORTANT**: CLI tools update frequently. ALWAYS run `--help` for the specific command BEFORE using it to verify current syntax.

**GitLab** (if PLATFORM=gitlab):

```bash
# Fetch MR details with comments in one call
glab mr view <MR_NUMBER> --comments --output json

# If you're NOT in the repo directory, add --repo flag:
glab mr view <MR_NUMBER> --comments --output json --repo <owner>/<repo>
```

**GitHub** (if PLATFORM=github):

```bash
# Fetch PR details with comments
gh pr view <PR_NUMBER> --json number,title,body,headRefName,headRefOid,url,comments

# If you're NOT in the repo directory, add --repo flag:
gh pr view <PR_NUMBER> --json number,title,body,headRefName,headRefOid,url,comments --repo <owner>/<repo>
```

**3. Delegate to Agents with JSON Output**

⚠️ **CRITICAL**: You MUST include the exact string "OUTPUT_FORMAT=JSON" in your delegation prompt to both agents.

**Example delegation prompt:**

```
OUTPUT_FORMAT=JSON

Review the code changes in MR/PR #123...
[rest of your prompt]
```

Without "OUTPUT_FORMAT=JSON", agents will output markdown instead of JSON, and the format-review script will fail.

Pass the following context to agents:

- **OUTPUT_FORMAT=JSON** (MANDATORY - must be first line of prompt)
- MR/PR metadata (number, title, source branch, commit SHA)
- List of existing comments (if any) with their content and line references
- Request agent to verify if existing comments have been addressed in current code

## Review Workflow:

1. **Determine Review Scope**
   - Check git status to identify changed files
   - Parse arguments to see if user requested specific review aspects
   - Default: Run all applicable reviews
2. **Available Review Aspects:**
   - **comments** - Analyze code comment accuracy and maintainability
   - **tests** - Review test coverage quality and completeness
   - **errors** - Check error handling for silent failures
   - **types** - Analyze type design and invariants (if new types added)
   - **code** - General code review for project guidelines
   - **simplify** - Simplify code for clarity and maintainability
   - **all** - Run all applicable reviews (default)
3. **Identify Changed Files**
   - Run `git diff --name-only` to see modified files
   - Check if PR/MR already exists: `gh pr view` or `glab mr view``
   - Identify file types and what reviews apply

## After Agent Reviews Complete:

**4. Validate Agent JSON Output**

Before formatting, verify that both agents returned valid JSON:

```bash
# Test if agent output is valid JSON
printf '%s' "$CODE_REVIEW_JSON" | jq empty
printf '%s' "$ARCH_REVIEW_JSON" | jq empty

# Check for required fields
printf '%s' "$CODE_REVIEW_JSON" | jq -e '.type == "code" and has("verdict")' >/dev/null
printf '%s' "$ARCH_REVIEW_JSON" | jq -e '.type == "architecture"' >/dev/null
```

**IMPORTANT**: Use `printf '%s'` instead of `echo` to avoid interpretation issues with backticks.

If validation fails:

- Agent likely output markdown instead of JSON
- Check that "OUTPUT_FORMAT=JSON" was in delegation prompt
- Re-run agents with correct prompt

**5. Format Review Comments**

Both `code-reviewer` and `software-architect` agents output **structured JSON**. Use the `format-review` script to generate consistent markdown comments.

**CRITICAL - JSON Passing Patterns:**

⚠️ **NEVER** pass JSON as command-line argument - it will fail with escape errors!
✅ **ALWAYS** pipe to stdin using the `-` argument

**Choose the correct pattern based on your situation:**

### Pattern A: When you have JSON in a bash variable (from agent output)

```bash
# Step 1: Locate the VCS tool
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

# Step 2: Get JSON from code-reviewer agent (example variable)
CODE_REVIEW_JSON='{"type":"code","verdict":"PASS",...}'

# Step 3: Format code review - use printf to avoid backtick interpretation
CODE_COMMENT=$(printf '%s' "$CODE_REVIEW_JSON" | "$VCS_TOOL" format-review -)

# Step 4: Get JSON from software-architect agent
ARCH_REVIEW_JSON='{"type":"architecture","concerns":[...]}'

# Step 5: Format architecture review
ARCH_COMMENT=$(printf '%s' "$ARCH_REVIEW_JSON" | "$VCS_TOOL" format-review -)

# Step 6: Combine both formatted comments
FINAL_COMMENT="$CODE_COMMENT

---

$ARCH_COMMENT"
```

**Why `printf '%s'` instead of `echo`?**

- `printf '%s'` outputs the variable exactly as-is without interpretation
- `echo` may interpret escape sequences and cause issues
- This prevents bash from treating backticks in JSON as command substitution

### Pattern B: When you're testing with literal JSON (for examples/debugging)

```bash
# Use heredoc with single quotes for literal JSON
CODE_COMMENT=$(cat <<'EOF_CODE' | "$VCS_TOOL" format-review -
{
  "type": "code",
  "verdict": "PASS",
  "critical": [],
  "warnings": [],
  "suggestions": []
}
EOF_CODE
)
```

**Heredoc Pattern Explanation:**

- `cat <<'EOF_CODE'` - Start heredoc (single quotes prevent variable expansion)
- Paste the entire JSON object here (can be multiple lines)
- `EOF_CODE` - End heredoc marker
- `| "$VCS_TOOL" format-review -` - Pipe to script, `-` means read from stdin
- `$(...)` - Capture output in variable

**Why Use format-review Script?**

- ✅ **100% Consistent formatting** - identical output every time
- ✅ **No template interpretation** - agents output JSON, script formats
- ✅ **Automatic section skipping** - empty sections omitted
- ✅ **Validated structure** - ensures required fields exist

**6. Post Review Comment**

After formatting, **ask user** if they want to publish the comment to MR/PR.

**MANDATORY**: Verify formatted output is not empty before asking to post:

```bash
# Check if formatted output has content
if [ -z "$FINAL_COMMENT" ] || [ "$FINAL_COMMENT" = "" ]; then
  echo "ERROR: Formatted review is empty. Check agent JSON output."
  exit 1
fi
```

**IMPORTANT**: Always use the `post-comment` command (never use `glab` or `gh` directly):

```bash
# Step 1: Locate the VCS tool (if not already set)
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

# Step 2: Detect platform (if not already set)
PLATFORM=$("$VCS_TOOL" detect-platform)

# Step 3: Post the comment using the full URL from $ARGUMENTS
# The post-comment script will automatically extract repo info and MR/PR number from the URL
# It also supports just a number if you're in the correct repo directory
echo "$FINAL_COMMENT" | "$VCS_TOOL" post-comment "$PLATFORM" "$ARGUMENTS" -
```

**Why use post-comment instead of glab/gh directly?**

- ✅ Unified interface for both GitLab and GitHub
- ✅ Proper stdin handling for long comments (no escaping issues)
- ✅ Automatic repo detection from URL (works regardless of current directory)
- ✅ Consistent error messages
- ✅ Centralized with other VCS operations

**Important Notes**:

- Always use stdin with `-` for formatted reviews (they're long and multiline)
- DON'T publish automatically - always ask user first!
- The command handles platform differences and repo extraction automatically
- Passing the full URL is recommended (script will extract repo owner/name and MR/PR number)
