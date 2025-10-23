---
name: Atlassian Admin
description: Manage Jira and Confluence via REST API. ALWAYS use when user mentions Jira, Confluence, issues, sprints, wiki pages, or Atlassian URLs. Handles reading articles, managing issues, sprint planning, and knowledge base operations.
allowed-tools: Bash, Read, Grep, WebFetch, BashOutput, KillShell
---

# Atlassian Admin

Manage Jira and Confluence via REST API with auto-discovery from ~/.secrets.

## Core Capabilities

**Jira:**

1. Search/list issues (JQL support)
2. Read issue details (full data + comments)
3. Create/update issues
4. Sprint management

**Confluence:**

1. Read pages/articles
2. Search content (CQL support)
3. Create/update pages
4. List spaces/pages

## When to Use

Invoke when user mentions:

- Jira or Confluence URLs
- Issues, tasks, tickets, sprints
- Wiki pages, articles, knowledge base
- Searching/reading Atlassian content

## Prerequisites

**Environment Variables (in ~/.secrets):**

Pattern: `JIRA_<COMPANY>_URL`, `JIRA_<COMPANY>_TOKEN`, `CONFLUENCE_<COMPANY>_URL`, `CONFLUENCE_<COMPANY>_TOKEN`

Example (4RA):

```bash
export JIRA_4RA_URL="https://jira.deversin.com"
export JIRA_4RA_TOKEN="your-token-here"
export CONFLUENCE_4RA_URL="https://confluence.deversin.com"
export CONFLUENCE_4RA_TOKEN="your-token-here"
```

**Python:** Python 3 (uses urllib, no extra deps)

## Finding the Tool

**Auto-discover:**

```bash
ATLASSIAN_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/atlassian-admin/atlassian-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)
```

**Direct (faster):**

```bash
ATLASSIAN_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/atlassian-admin/atlassian-tool.sh
```

## Quick Reference

### Discovery

```bash
"$ATLASSIAN_TOOL" discover
```

Returns all available Jira/Confluence instances.

### Jira - Search Issues

```bash
"$ATLASSIAN_TOOL" jira-search 4RA "project = DEV AND status = 'In Progress'"
```

Returns JSON array of issues.

### Jira - Get Issue

```bash
"$ATLASSIAN_TOOL" jira-get-issue 4RA "DEV-123"
```

Returns full issue JSON with fields, comments, attachments.

### Jira - Create Issue

```bash
cat <<'EOF' | "$ATLASSIAN_TOOL" jira-create-issue 4RA -
{
  "project": {"key": "DEV"},
  "summary": "Fix authentication bug",
  "issuetype": {"name": "Bug"},
  "description": "Users unable to login"
}
EOF
```

### Jira - Update Issue

```bash
cat <<'EOF' | "$ATLASSIAN_TOOL" jira-update-issue 4RA "DEV-123" -
{
  "fields": {
    "status": {"name": "Done"}
  },
  "update": {
    "comment": [{"add": {"body": "Fixed in PR #456"}}]
  }
}
EOF
```

### Jira - List Sprints

```bash
"$ATLASSIAN_TOOL" jira-list-sprints 4RA 10
```

List sprints for board ID 10.

### Jira - Get Sprint

```bash
"$ATLASSIAN_TOOL" jira-get-sprint 4RA 42
```

Get sprint details including issues.

### Confluence - Get Page

```bash
"$ATLASSIAN_TOOL" confluence-get-page 4RA --url "https://confluence.deversin.com/display/DEV/Release+Notes"

"$ATLASSIAN_TOOL" confluence-get-page 4RA --space DEV --title "Release Notes"
```

Returns page content with metadata.

### Confluence - Search

```bash
"$ATLASSIAN_TOOL" confluence-search 4RA "type=page AND space=DEV AND text~'API'"
```

Search using CQL.

### Confluence - Create Page

```bash
cat <<'EOF' | "$ATLASSIAN_TOOL" confluence-create-page 4RA -
{
  "type": "page",
  "title": "API Documentation",
  "space": {"key": "DEV"},
  "body": {
    "storage": {
      "value": "<p>API docs here</p>",
      "representation": "storage"
    }
  }
}
EOF
```

### Confluence - Update Page

```bash
cat <<'EOF' | "$ATLASSIAN_TOOL" confluence-update-page 4RA "123456" -
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

### Confluence - List Spaces

```bash
"$ATLASSIAN_TOOL" confluence-list-spaces 4RA
```

### Confluence - List Pages

```bash
"$ATLASSIAN_TOOL" confluence-list-pages 4RA DEV
```

List all pages in DEV space.

## Workflow Example

```bash
ATLASSIAN_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/atlassian-admin/atlassian-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

INSTANCES=$("$ATLASSIAN_TOOL" discover)
echo "$INSTANCES" | jq

ISSUES=$("$ATLASSIAN_TOOL" jira-search 4RA "project = DEV ORDER BY created DESC")
echo "$ISSUES" | jq -r '.issues[] | "\(.key): \(.fields.summary)"'
```

## Integration

- All commands return JSON for easy parsing
- Auto-discovers all JIRA*\* and CONFLUENCE*\* from ~/.secrets
- Supports multiple companies/instances
- Uses REST API v2 (Jira) and v1 (Confluence)

## Key Points

✅ Auto-discovery from ~/.secrets (JIRA*\*/CONFLUENCE*\* pattern)
✅ JQL and CQL query support
✅ Full CRUD operations
✅ JSON I/O for all commands
✅ Multi-instance support (future-proof)

---

**For detailed API docs, see [commands.md](commands.md)**
