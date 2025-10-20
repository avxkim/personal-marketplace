Creates a pull request (GitHub) or merge request (GitLab) with standardized format using automated Python script.

python ${CLAUDE_PLUGIN_ROOT}/commands/scripts/create_pr.py $ARGUMENTS

**Arguments**: `$ARGUMENTS` should contain:

- No args: Current branch → default branch
- One arg: Current branch → specified target
- Two args: source → target
- Three args: source → target assignee

**Features**:

- Auto-detects GitHub or GitLab platform
- Extracts task ID from branch name (TEC-999, TASK-123, etc.)
- Generates title: `TASK-123: description` or `feat/fix: description`
- Adds "Closes: TASK-ID" to description
- Handles nested git repositories automatically
- Creates PR/MR only in repos with changes
