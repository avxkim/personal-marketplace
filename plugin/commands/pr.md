Creates PR/MR with task ID extraction and standardized format. Source branch is always preserved.

python ${CLAUDE_PLUGIN_ROOT}/commands/scripts/create_pr.py $ARGUMENTS

**Arguments**:

- No args: current → default branch
- One arg: current → target
- Two args: source → target
- Three args: source → target assignee

**Behavior**:

- Title: `TASK-123: description` or `feat/fix: description`
- Description: `Closes: TASK-ID` (if task ID found)
- Source branch: never deleted
- Nested repos: handled automatically
