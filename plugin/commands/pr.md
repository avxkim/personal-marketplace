## Create Pull/Merge Request

Creates a pull request (GitHub) or merge request (GitLab) with standardized format.

**Arguments**: `$ARGUMENTS` should contain source and target branches (e.g., "feature-branch main" or just "main" to use current branch) and optionally assignee

### Workflow:

1. **Detect platform**: Check if repo uses GitHub or GitLab
2. **Parse arguments**:
   - If three args: first is source, second is target, thirs is assignee
   - If two args: first is source, second is target
   - If one arg: current branch is source, arg is target
   - If no args: current branch is source, default/master is target
3. **Extract task ID**: Look for task pattern in branch name (e.g., TEC-999, TASK-123)
4. **Generate title**: Follow pattern from branch name or recent commits
5. **Generate description**: Include "Closes: TASK-ID" if task ID found
6. **Create PR/MR**: Use appropriate CLI tool

### Title Format:
- If branch has task ID: `TASK-123: Brief description`
- Otherwise: `feat/fix/chore: brief description`, just like gitflow naming conventions, but with lowercase only

### Description Template:
```
Closes: TASK-123
``

Don't add anything more than i mentioned in above template!`

### Commands to use:

**GitLab (glab):**
```bash
# First, check current version help for accurate syntax
glab mr create --help

# Create MR
glab mr create \
  --source-branch <source> \
  --target-branch <target> \
  --title "TASK-123: Title" \
  --description "$(cat <<'EOF'
Description here
EOF
)" \
  --remove-source-branch
```

**GitHub (gh):**
```bash
# First, check current version help for accurate syntax
gh pr create --help

# Create PR
gh pr create \
  --base <target> \
  --head <source> \
  --title "TASK-123: Title" \
  --body "$(cat <<'EOF'
Description here
EOF
)"
```

### Important:
- ALWAYS run `glab mr create --help` or `gh pr create --help` first to check current syntax
- Use `git log --oneline -5` to extract task IDs and commit messages
- If task ID exists in branch name, it MUST be in the title and description
- Check if project has nested git repos, for example `layers` directory, it might have separate git repos, where you have to check, if anything was changed, you should create MR/PR here too!
