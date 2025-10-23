# Atlassian Admin - Command Reference

Concise API reference for all commands.

## Discovery

### discover

List all available Jira/Confluence instances from ~/.secrets.

```bash
"$ATLASSIAN_TOOL" discover
```

**Output:**

```json
[
  {
    "instance": "4RA",
    "services": {
      "jira": { "url": "https://jira.deversin.com", "configured": true },
      "confluence": {
        "url": "https://confluence.deversin.com",
        "configured": true
      }
    }
  }
]
```

## Jira Commands

### jira-search

Search issues using JQL (Jira Query Language).

```bash
"$ATLASSIAN_TOOL" jira-search <instance> "<jql>" [options]
```

**Options:**

- `--max-results N` - Max results (default: 50)
- `--start-at N` - Start at index (default: 0)
- `--fields "field1,field2"` - Specific fields to return

**Examples:**

```bash
"$ATLASSIAN_TOOL" jira-search 4RA "project = DEV AND status = 'In Progress'"
"$ATLASSIAN_TOOL" jira-search 4RA "assignee = currentUser() ORDER BY created DESC" --max-results 10
"$ATLASSIAN_TOOL" jira-search 4RA "sprint in openSprints()" --fields "summary,status,assignee"
```

### jira-get-issue

Get full issue details including fields, comments, attachments.

```bash
"$ATLASSIAN_TOOL" jira-get-issue <instance> <issue-key> [options]
```

**Options:**

- `--fields "field1,field2"` - Specific fields
- `--expand "option1,option2"` - Expand options (e.g., changelog, renderedFields)

**Examples:**

```bash
"$ATLASSIAN_TOOL" jira-get-issue 4RA "DEV-123"
"$ATLASSIAN_TOOL" jira-get-issue 4RA "DEV-123" --expand "changelog,renderedFields"
```

### jira-create-issue

Create new issue.

```bash
cat <<'EOF' | "$ATLASSIAN_TOOL" jira-create-issue <instance> -
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
cat <<'EOF' | "$ATLASSIAN_TOOL" jira-update-issue <instance> <issue-key> -
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
cat <<'EOF' | "$ATLASSIAN_TOOL" jira-update-issue 4RA "DEV-123" -
{
  "transition": {"id": "31"}
}
EOF
```

### jira-list-sprints

List sprints for a board.

```bash
"$ATLASSIAN_TOOL" jira-list-sprints <instance> <board-id> [options]
```

**Options:**

- `--state <state>` - Filter by state: future, active, closed
- `--max-results N` - Max results (default: 50)

**Examples:**

```bash
"$ATLASSIAN_TOOL" jira-list-sprints 4RA 10
"$ATLASSIAN_TOOL" jira-list-sprints 4RA 10 --state active
```

### jira-get-sprint

Get sprint details including issues.

```bash
"$ATLASSIAN_TOOL" jira-get-sprint <instance> <sprint-id>
```

## Confluence Commands

### confluence-get-page

Get page content by URL, page ID, or space/title.

```bash
"$ATLASSIAN_TOOL" confluence-get-page <instance> --url <url>
"$ATLASSIAN_TOOL" confluence-get-page <instance> --page-id <id>
"$ATLASSIAN_TOOL" confluence-get-page <instance> --space <key> --title <title>
```

**Options:**

- `--url` - Full page URL
- `--page-id` - Numeric page ID
- `--space` + `--title` - Space key and page title
- `--expand` - Expand options (default: body.storage,version)

**Examples:**

```bash
"$ATLASSIAN_TOOL" confluence-get-page 4RA --url "https://confluence.deversin.com/display/DEV/API"
"$ATLASSIAN_TOOL" confluence-get-page 4RA --page-id "123456"
"$ATLASSIAN_TOOL" confluence-get-page 4RA --space DEV --title "API Documentation"
```

### confluence-search

Search content using CQL (Confluence Query Language).

```bash
"$ATLASSIAN_TOOL" confluence-search <instance> "<cql>" [options]
```

**Options:**

- `--limit N` - Max results (default: 25)
- `--start N` - Start at index (default: 0)
- `--expand` - Expand options

**Examples:**

```bash
"$ATLASSIAN_TOOL" confluence-search 4RA "type=page AND space=DEV"
"$ATLASSIAN_TOOL" confluence-search 4RA "text~'API' AND space=DEV"
"$ATLASSIAN_TOOL" confluence-search 4RA "label=documentation"
```

### confluence-create-page

Create new page.

```bash
cat <<'EOF' | "$ATLASSIAN_TOOL" confluence-create-page <instance> -
{
  "type": "page",
  "title": "Page Title",
  "space": {"key": "DEV"},
  "body": {
    "storage": {
      "value": "<p>Page content in storage format</p>",
      "representation": "storage"
    }
  }
}
EOF
```

**With Parent Page:**

```bash
cat <<'EOF' | "$ATLASSIAN_TOOL" confluence-create-page 4RA -
{
  "type": "page",
  "title": "Child Page",
  "space": {"key": "DEV"},
  "ancestors": [{"id": "123456"}],
  "body": {
    "storage": {
      "value": "<p>Content here</p>",
      "representation": "storage"
    }
  }
}
EOF
```

### confluence-update-page

Update existing page.

```bash
cat <<'EOF' | "$ATLASSIAN_TOOL" confluence-update-page <instance> <page-id> -
{
  "version": {"number": 2},
  "title": "Updated Title",
  "type": "page",
  "body": {
    "storage": {
      "value": "<p>Updated content</p>",
      "representation": "storage"
    }
  }
}
EOF
```

**Note:** Must increment `version.number` from current version.

### confluence-list-spaces

List all spaces.

```bash
"$ATLASSIAN_TOOL" confluence-list-spaces <instance> [options]
```

**Options:**

- `--limit N` - Max results (default: 25)
- `--start N` - Start at index (default: 0)
- `--type` - Space type: global, personal

**Examples:**

```bash
"$ATLASSIAN_TOOL" confluence-list-spaces 4RA
"$ATLASSIAN_TOOL" confluence-list-spaces 4RA --type global
```

### confluence-list-pages

List pages in a space.

```bash
"$ATLASSIAN_TOOL" confluence-list-pages <instance> <space-key> [options]
```

**Options:**

- `--limit N` - Max results (default: 25)
- `--start N` - Start at index (default: 0)
- `--expand` - Expand options

**Examples:**

```bash
"$ATLASSIAN_TOOL" confluence-list-pages 4RA DEV
"$ATLASSIAN_TOOL" confluence-list-pages 4RA DEV --expand "body.view,version"
```

## Environment Variables

**Pattern:**

```bash
JIRA_<COMPANY>_URL
JIRA_<COMPANY>_TOKEN
CONFLUENCE_<COMPANY>_URL
CONFLUENCE_<COMPANY>_TOKEN
```

**Example (4RA):**

```bash
export JIRA_4RA_URL="https://jira.deversin.com"
export JIRA_4RA_TOKEN="base64-encoded-token"
export CONFLUENCE_4RA_URL="https://confluence.deversin.com"
export CONFLUENCE_4RA_TOKEN="base64-encoded-token"
```

## Exit Codes

- `0` - Success
- `1` - Error (missing env vars, API error, invalid input)

## Notes

**JQL Resources:**

- [JQL Reference](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
- Common: `project = KEY`, `status = "In Progress"`, `assignee = currentUser()`, `sprint in openSprints()`

**CQL Resources:**

- [CQL Reference](https://developer.atlassian.com/server/confluence/advanced-searching-using-cql/)
- Common: `type=page`, `space=KEY`, `text~"keyword"`, `label=tag`

**Confluence Storage Format:**

- HTML-based format for page content
- Use `<p>`, `<h1>`, `<ul>`, etc.
- For complex formatting, copy from existing pages
