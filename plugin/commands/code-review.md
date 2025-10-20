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

When delegating to `code-reviewer` and `software-architect` agents, include "OUTPUT_FORMAT=JSON" in your prompt to trigger JSON-only output mode.

Pass the following context:

- **OUTPUT_FORMAT=JSON** (required for formatting script to work)
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

**4. Format Review Comments**

Both `code-reviewer` and `software-architect` agents output **structured JSON**. Use the `format-review` script to generate consistent markdown comments.

**CRITICAL - MUST Use Heredoc Pattern:**

⚠️ **DO NOT** pass JSON as command-line argument - it will fail with escape errors!
✅ **ALWAYS** use heredoc with stdin (the `-` argument tells script to read from stdin)

```bash
# Step 1: Locate the VCS tool
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

# Step 2: Format code review JSON
# IMPORTANT: Use heredoc (cat <<'EOF' | command -) to pass JSON via stdin
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

# Step 3: Format architecture review JSON
# IMPORTANT: Use heredoc (cat <<'EOF' | command -) to pass JSON via stdin
ARCH_COMMENT=$(cat <<'EOF_ARCH' | "$VCS_TOOL" format-review -
{
  "type": "architecture",
  "strengths": [],
  "concerns": [],
  "compliance": []
}
EOF_ARCH
)

# Step 4: Combine both formatted comments
FINAL_COMMENT="$CODE_COMMENT

---

$ARCH_COMMENT"
```

**Pattern Explanation:**

- `cat <<'EOF_CODE'` - Start heredoc (the quotes prevent variable expansion)
- Paste the entire JSON object here (can be multiple lines)
- `EOF_CODE` - End heredoc marker
- `| "$VCS_TOOL" format-review -` - Pipe to script, `-` means read from stdin
- `$(...)` - Capture output in variable

**Why Use format-review Script?**

- ✅ **100% Consistent formatting** - identical output every time
- ✅ **No template interpretation** - agents output JSON, script formats
- ✅ **Automatic section skipping** - empty sections omitted
- ✅ **Validated structure** - ensures required fields exist

**5. Post Review Comment**

After formatting, **ask user** if they want to publish the comment to MR/PR.

**IMPORTANT**: Always use the `post-comment` command (never use `glab` or `gh` directly):

```bash
# Step 1: Locate the VCS tool (if not already set)
VCS_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/vcs-tool-manager/vcs-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

# Step 2: Detect platform (if not already set)
PLATFORM=$("$VCS_TOOL" detect-platform)

# Step 3: Extract issue number from MR/PR URL or use the number directly
# For GitLab: extract from URL like https://gitlab.com/owner/repo/-/merge_requests/123
# For GitHub: extract from URL like https://github.com/owner/repo/pull/123
# Or if $ARGUMENTS is just a number, use it directly
ISSUE_NUMBER=$(echo "$ARGUMENTS" | grep -oE '[0-9]+' | tail -1)

# Step 4: Post the comment
echo "$FINAL_COMMENT" | "$VCS_TOOL" post-comment "$PLATFORM" "$ISSUE_NUMBER" -
```

**Why use post-comment instead of glab/gh directly?**

- ✅ Unified interface for both GitLab and GitHub
- ✅ Proper stdin handling for long comments (no escaping issues)
- ✅ Consistent error messages
- ✅ Centralized with other VCS operations

**Important Notes**:

- Always use stdin with `-` for formatted reviews (they're long and multiline)
- DON'T publish automatically - always ask user first!
- The command handles platform differences automatically
