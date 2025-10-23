---
name: Jira Admin
description: Manage Jira via REST API. ALWAYS use when user mentions Jira, issues, tickets, sprints, or Jira URLs. Handles reading issues, managing tickets, sprint planning, and JQL queries.
allowed-tools: Bash, Read, Grep, WebFetch, BashOutput, KillShell
---

# Jira Admin

Manage Jira via REST API with auto-discovery from ~/.secrets.

## Core Capabilities

**Jira:**

1. Search/list issues (JQL support)
2. Read issue details (full data + comments)
3. Create/update issues
4. Sprint management

## When to Use

Invoke when user mentions:

- Jira URLs
- Issues, tasks, tickets, sprints
- Searching/reading Jira content
- JQL queries

## Prerequisites

**Environment Variables (in ~/.secrets):**

Pattern: `JIRA_<COMPANY>_URL`, `JIRA_<COMPANY>_TOKEN`

Example (4RA):

```bash
export JIRA_4RA_URL="https://jira.deversin.com"
export JIRA_4RA_TOKEN="your-bearer-token-here"
```

**Python:** Python 3 (uses urllib, no extra deps)

## Finding the Tool

**Auto-discover:**

```bash
JIRA_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/jira-admin/jira-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)
```

**Direct (faster):**

```bash
JIRA_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/jira-admin/jira-tool.sh
```

## Quick Reference

### Discovery

```bash
"$JIRA_TOOL" discover
```

Returns all available Jira instances.

### Jira - Search Issues

```bash
"$JIRA_TOOL" jira-search 4RA "project = DEV AND status = 'In Progress'"
```

Returns JSON array of issues.

### Jira - Get Issue

```bash
"$JIRA_TOOL" jira-get-issue 4RA "DEV-123"
```

Returns full issue JSON with fields, comments, attachments.

### Jira - Create Issue

```bash
cat <<'EOF' | "$JIRA_TOOL" jira-create-issue 4RA -
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
cat <<'EOF' | "$JIRA_TOOL" jira-update-issue 4RA "DEV-123" -
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
"$JIRA_TOOL" jira-list-sprints 4RA 10
```

List sprints for board ID 10.

### Jira - Get Sprint

```bash
"$JIRA_TOOL" jira-get-sprint 4RA 42
```

Get sprint details including issues.

## Workflow Example

```bash
JIRA_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/jira-admin/jira-tool.sh

INSTANCES=$("$JIRA_TOOL" discover)
echo "$INSTANCES" | jq

ISSUES=$("$JIRA_TOOL" jira-search 4RA "project = DEV ORDER BY created DESC")
echo "$ISSUES" | jq -r '.issues[] | "\(.key): \(.fields.summary)"'
```

## Integration

- All commands return JSON for easy parsing
- Auto-discovers all JIRA\_\* tokens from ~/.secrets
- Supports multiple companies/instances
- Uses REST API v2 (Jira)
- Uses Bearer token authentication

## Key Points

✅ Auto-discovery from ~/.secrets (JIRA\_\* pattern)
✅ JQL query support
✅ Full CRUD operations
✅ JSON I/O for all commands
✅ Multi-instance support
✅ Bearer token authentication (no nginx auth required)

---

**For detailed API docs, see [commands.md](commands.md)**
