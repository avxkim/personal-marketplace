# Jira Admin - Command Reference

Concise API reference for all Jira commands.

## Discovery

### discover

List all available Jira instances from ~/.secrets.

```bash
"$JIRA_TOOL" discover
```

**Output:**

```json
[
  {
    "instance": "4RA",
    "services": {
      "jira": { "url": "https://jira.deversin.com", "configured": true }
    }
  }
]
```

## Jira Commands

### jira-search

Search issues using JQL (Jira Query Language).

```bash
"$JIRA_TOOL" jira-search <instance> "<jql>" [options]
```

**Options:**

- `--max-results N` - Max results (default: 50)
- `--start-at N` - Start at index (default: 0)
- `--fields "field1,field2"` - Specific fields to return

**Examples:**

```bash
"$JIRA_TOOL" jira-search 4RA "project = DEV AND status = 'In Progress'"
"$JIRA_TOOL" jira-search 4RA "assignee = currentUser() ORDER BY created DESC" --max-results 10
"$JIRA_TOOL" jira-search 4RA "sprint in openSprints()" --fields "summary,status,assignee"
```

### jira-get-issue

Get full issue details including fields, comments, attachments.

```bash
"$JIRA_TOOL" jira-get-issue <instance> <issue-key> [options]
```

**Options:**

- `--fields "field1,field2"` - Specific fields
- `--expand "option1,option2"` - Expand options (e.g., changelog, renderedFields)

**Examples:**

```bash
"$JIRA_TOOL" jira-get-issue 4RA "DEV-123"
"$JIRA_TOOL" jira-get-issue 4RA "DEV-123" --expand "changelog,renderedFields"
```

### jira-create-issue

Create new issue.

```bash
cat <<'EOF' | "$JIRA_TOOL" jira-create-issue <instance> -
{
  "project": {"key": "DEV"},
  "summary": "Issue title",
  "issuetype": {"name": "Bug"},
  "description": "Description here",
  "priority": {"name": "High"}
}
EOF
```

**Required Fields:**

- `project.key` - Project key
- `summary` - Issue title
- `issuetype.name` - Bug, Task, Story, etc.

**Optional Fields:**

- `description` - Issue description
- `priority.name` - Highest, High, Medium, Low, Lowest
- `assignee.name` - Username
- `labels` - Array of labels
- `components` - Array of component objects

### jira-update-issue

Update issue fields or add comments.

```bash
cat <<'EOF' | "$JIRA_TOOL" jira-update-issue <instance> <issue-key> -
{
  "fields": {
    "summary": "Updated title",
    "description": "Updated description"
  },
  "update": {
    "comment": [{"add": {"body": "Adding a comment"}}]
  }
}
EOF
```

**Transition Example:**

```bash
cat <<'EOF' | "$JIRA_TOOL" jira-update-issue 4RA "DEV-123" -
{
  "transition": {"id": "31"}
}
EOF
```

### jira-list-sprints

List sprints for a board.

```bash
"$JIRA_TOOL" jira-list-sprints <instance> <board-id> [options]
```

**Options:**

- `--state <state>` - Filter by state: future, active, closed
- `--max-results N` - Max results (default: 50)

**Examples:**

```bash
"$JIRA_TOOL" jira-list-sprints 4RA 10
"$JIRA_TOOL" jira-list-sprints 4RA 10 --state active
```

### jira-get-sprint

Get sprint details including issues.

```bash
"$JIRA_TOOL" jira-get-sprint <instance> <sprint-id>
```

**Example:**

```bash
"$JIRA_TOOL" jira-get-sprint 4RA 42
```

## Authentication

Uses Bearer token authentication (no nginx auth required).

**Token Format:** Base64-encoded `userid:api_token`

Set in `~/.secrets`:

```bash
export JIRA_4RA_URL="https://jira.deversin.com"
export JIRA_4RA_TOKEN="your-bearer-token-here"
```

## JQL Quick Reference

Common JQL queries:

```jql
project = DEV
status = "In Progress"
assignee = currentUser()
sprint in openSprints()
created >= -7d
updated >= -1h
priority in (High, Highest)
labels = "bug"
```

Operators: `=`, `!=`, `>`, `<`, `>=`, `<=`, `IN`, `NOT IN`, `~` (contains), `!~` (not contains)

Combine with: `AND`, `OR`, `NOT`

Order by: `ORDER BY created DESC`, `ORDER BY priority ASC`
