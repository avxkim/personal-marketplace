## Code review guidance

- MR/PR url: $ARGUMENTS
- **Working Directory**: Agents will check current directory first and only clone if necessary
- ALWAYS delegate review to `code-reviewer` agent with the MR/PR URL from $ARGUMENTS
- The `code-reviewer` agent will fetch MR/PR details, diff, and any existing comments itself
- The `code-reviewer` agent will use the `avx:vcs-tool-manager` skill to generate validated line links automatically
- The `code-reviewer` agent will verify line numbers before generating links (uses grep -n and file reads, not just git diff positions)
- The code-reviewer agent will provide PASS/FAIL verdict, `software-architect` agent should run in parallel with `code-reviewer`

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

After thorough review, ask if you should write a comment on the MR/PR page.
Don't add "reviewed by", review dates in the footer of the comment.
Use the following comment template based on code-reviewer agent output (STRICTLY FOLLOW THIS TEMPLATE!):

# Code Review Summary 🔍

## 🔴 Critical Issues (Must Fix)

1. **Filename** ([FILENAME:LINE](https://gitdomain.com)):
   Issue description

---

## 🟡 Warnings (Should Fix)

1. **Filename** ([FILENAME:LINE](https://gitdomain.com)):
   Issue description

---

## 🟢 Suggestions (Consider)

1. **Filename** ([FILENAME:LINE](https://gitdomain.com)):
   Issue description

---

## ✅ Verdict

**PASS** ✔️ - Ready for merge
OR
**FAIL** ❌ - Requires fixes before merge

## Post review actions

- When `code-review` is finished review process, ask me if i want to publish that comment, DON'T publish automatically!

## Template guidelines

- **Filename** - must be in bold text, not as heading
- **FILENAME:LINE** - must be a clickable link to exact line (e.g., https://gitlab.com/repo/file.js#L42). The `code-reviewer` agent will use the `avx:vcs-tool-manager` skill to generate these links with verified, accurate line numbers (not git diff positions).
- Link should point to the source branch being reviewed (the skill handles this automatically)
- Issue descriptions should be clear and actionable
- Only include sections that have issues (skip empty sections)
- Use emojis for visual clarity and better readability
- If all checks pass with no issues, just post the PASS verdict
