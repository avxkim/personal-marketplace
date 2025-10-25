---
name: Confluence Admin
description: Manage Confluence via REST API. ALWAYS use when user mentions Confluence, wiki pages, or Confluence URLs. Supports both nginx-protected instances (browser auth) and normal instances (PAT/password auth). Handles reading pages, searching, creating/updating content, and managing attachments.
allowed-tools: Bash, Read, Grep, WebFetch, BashOutput, KillShell
---

# Confluence Admin

Manage Confluence via REST API with smart authentication detection.

## Core Capabilities

**Spaces:**

1. List all spaces (global/personal)
2. Get space details

**Pages:**

1. Get page by ID (with content, version, history)
2. Search pages using CQL (Confluence Query Language)
3. Create new pages
4. Update existing pages

**Attachments:**

1. List page attachments
2. Get attachment details

## When to Use

Invoke when user mentions:

- Confluence URLs
- Wiki pages, documentation, knowledge base
- Searching Confluence content
- Creating/updating Confluence pages
- CQL queries

## Prerequisites

**Environment Variables (in ~/.secrets):**

### For Normal Confluence (PAT-based):

```bash
export CONFLUENCE_COMPANY_URL="https://confluence.company.com"
export CONFLUENCE_COMPANY_USERNAME="your_username"
export CONFLUENCE_COMPANY_PAT="your_personal_access_token"
```

### For nginx-Protected Confluence (browser auth):

```bash
export CONFLUENCE_DEVERSIN_URL="https://confluence.deversin.com"
export CONFLUENCE_DEVERSIN_USERNAME="alexandr_kim"
export CONFLUENCE_DEVERSIN_PASSWORD="your_password"
export CONFLUENCE_DEVERSIN_BASIC_USER="internal"  # nginx username
export CONFLUENCE_DEVERSIN_BASIC_PASS="nginx_password"  # nginx password
```

### For Password-based (no PAT):

```bash
export CONFLUENCE_ANOTHER_URL="https://confluence.another.com"
export CONFLUENCE_ANOTHER_USERNAME="username"
export CONFLUENCE_ANOTHER_PASSWORD="password"
```

**Python:** Python 3 (uses urllib, no extra deps for PAT/password auth)

**For nginx-protected instances:**

```bash
pip install playwright
playwright install chromium  # ~150MB, one-time download
```

## Authentication Methods

The tool automatically detects the authentication method based on environment variables:

1. **nginx-Protected (Browser Auth)**
   - Requires: `BASIC_USER` + `BASIC_PASS` + `USERNAME` + `PASSWORD`
   - Uses headless Chrome to login and get session cookie
   - Cookie cached for 7 days
   - Auto-refreshes on expiry

2. **PAT-based (Direct API)**
   - Requires: `USERNAME` + `PAT`
   - Direct API authentication
   - No browser needed
   - Instant access

3. **Password-based**
   - Requires: `USERNAME` + `PASSWORD`
   - Basic authentication
   - No browser needed

## Finding the Tool

**Auto-discover:**

```bash
CONFLUENCE_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/confluence-admin/confluence-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)
```

**Direct (faster):**

```bash
CONFLUENCE_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/confluence-admin/confluence-tool.sh
```

## Quick Reference

### Discovery

```bash
"$CONFLUENCE_TOOL" discover
```

Returns all available Confluence instances with auth types.

### List Spaces

```bash
"$CONFLUENCE_TOOL" list-spaces DEVERSIN 10 global
```

Lists spaces. Type: `global`, `personal`, or `all` (default).

### Get Space

```bash
"$CONFLUENCE_TOOL" get-space DEVERSIN "DEV"
```

Gets space details by key.

### Get Page

```bash
"$CONFLUENCE_TOOL" get-page DEVERSIN "123456" "body.storage,version"
```

Gets page with optional expansions.

### Search

```bash
"$CONFLUENCE_TOOL" search DEVERSIN "type=page AND space=DEV AND title~\"api\"" 25
```

Searches using CQL (Confluence Query Language).

### Create Page

```bash
cat <<'EOF' | "$CONFLUENCE_TOOL" create-page DEVERSIN -
{
  "type": "page",
  "title": "My New Page",
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

### Update Page

```bash
cat <<'EOF' | "$CONFLUENCE_TOOL" update-page DEVERSIN "123456" -
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

### List Attachments

```bash
"$CONFLUENCE_TOOL" list-attachments DEVERSIN "123456" 50
```

Lists attachments for a page.

## Workflow Example

```bash
CONFLUENCE_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/confluence-admin/confluence-tool.sh

INSTANCES=$("$CONFLUENCE_TOOL" discover)
echo "$INSTANCES" | jq

SPACES=$("$CONFLUENCE_TOOL" list-spaces DEVERSIN 10)
echo "$SPACES" | jq -r '.results[] | "\(.key): \(.name)"'

PAGES=$("$CONFLUENCE_TOOL" search DEVERSIN "type=page AND space=DEV" 10)
echo "$PAGES" | jq -r '.results[] | "\(.id): \(.title)"'
```

## Integration

- All commands return JSON for easy parsing
- Auto-discovers all CONFLUENCE\_\* instances from ~/.secrets
- Supports multiple companies/instances
- Uses REST API v1 (Data Center/Server compatible)
- Smart authentication: PAT, password, or browser session
- Auto-retry with session refresh on 401 errors

## Key Points

✅ Auto-discovery from ~/.secrets (CONFLUENCE\_\* pattern)
✅ CQL query support for advanced search
✅ Full CRUD operations for pages
✅ JSON I/O for all commands
✅ Multi-instance support
✅ Smart auth detection (PAT/password/nginx)
✅ Session caching for nginx instances (7-day TTL)
✅ Auto-refresh on session expiry

## Authentication Behavior

**First call to nginx instance:**

```
Authenticating to https://confluence.deversin.com...
✓ Authenticated successfully
[results...]
```

**Subsequent calls (cached):**

```
[results...]  # Instant, no browser launch
```

**After session expires:**

```
Session expired, clearing cache and retrying...
Authenticating to https://confluence.deversin.com...
✓ Authenticated successfully
[results...]
```

---

**For detailed API docs and examples, see [commands.md](commands.md)**
