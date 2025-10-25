## Confluence Admin - Command Reference

### Discovery

#### discover

List all configured Confluence instances.

**Usage:**

```bash
confluence-tool discover
```

**Output:**

```json
[
  {
    "name": "DEVERSIN",
    "url": "https://confluence.deversin.com",
    "username": "alexandr_kim",
    "auth_type": "nginx-protected (browser authentication)",
    "has_nginx": true,
    "has_pat": false,
    "has_password": true
  }
]
```

---

### Spaces

#### list-spaces

List spaces in Confluence.

**Usage:**

```bash
confluence-tool list-spaces <instance> [limit] [type]
```

**Arguments:**

- `instance`: Instance name (e.g., DEVERSIN)
- `limit`: Number of results (default: 25)
- `type`: Space type - `global`, `personal`, or `all` (default: all)

**Example:**

```bash
confluence-tool list-spaces DEVERSIN 10 global
```

#### get-space

Get space details by key.

**Usage:**

```bash
confluence-tool get-space <instance> <space_key>
```

**Example:**

```bash
confluence-tool get-space DEVERSIN "DEV"
```

---

### Pages

#### get-page

Get page by ID with optional expansions.

**Usage:**

```bash
confluence-tool get-page <instance> <page_id> [expand]
```

**Arguments:**

- `expand`: Comma-separated list of expansions
  - `body.storage` - Page content
  - `version` - Version info
  - `history` - Page history
  - `space` - Space details
  - `ancestors` - Parent pages

**Example:**

```bash
confluence-tool get-page DEVERSIN "123456" "body.storage,version,space"
```

#### search

Search Confluence using CQL (Confluence Query Language).

**Usage:**

```bash
confluence-tool search <instance> <cql_query> [limit]
```

**CQL Examples:**

- `type=page AND space=DEV` - All pages in DEV space
- `type=page AND title~"api"` - Pages with "api" in title
- `type=page AND creator=currentUser()` - Pages created by you
- `type=page AND lastModified > now("-7d")` - Pages modified in last 7 days
- `text~"authentication" AND space=DEV` - Pages containing "authentication"

**Example:**

```bash
confluence-tool search DEVERSIN 'type=page AND space=DEV AND title~"api"' 25
```

#### create-page

Create a new page.

**Usage:**

```bash
confluence-tool create-page <instance> <json_file|->
```

**JSON Structure:**

```json
{
  "type": "page",
  "title": "New Page Title",
  "space": { "key": "DEV" },
  "body": {
    "storage": {
      "value": "<p>Content in Confluence storage format</p>",
      "representation": "storage"
    }
  },
  "ancestors": [{ "id": "parent_page_id" }]
}
```

**Example (stdin):**

```bash
cat <<'EOF' | confluence-tool create-page DEVERSIN -
{
  "type": "page",
  "title": "API Documentation",
  "space": {"key": "DEV"},
  "body": {
    "storage": {
      "value": "<h1>API Endpoints</h1><p>List of all API endpoints...</p>",
      "representation": "storage"
    }
  }
}
EOF
```

**Example (file):**

```bash
confluence-tool create-page DEVERSIN page_data.json
```

#### update-page

Update an existing page.

**Usage:**

```bash
confluence-tool update-page <instance> <page_id> <json_file|->
```

**JSON Structure:**

```json
{
  "version": { "number": 2 },
  "title": "Updated Page Title",
  "type": "page",
  "body": {
    "storage": {
      "value": "<p>Updated content</p>",
      "representation": "storage"
    }
  }
}
```

**Note:** You must increment the version number. Get current version with `get-page`.

**Example:**

```bash
CURRENT_VERSION=$(confluence-tool get-page DEVERSIN "123456" "version" | jq '.version.number')
NEXT_VERSION=$((CURRENT_VERSION + 1))

cat <<EOF | confluence-tool update-page DEVERSIN "123456" -
{
  "version": {"number": $NEXT_VERSION},
  "title": "Updated API Docs",
  "type": "page",
  "body": {
    "storage": {
      "value": "<h1>Updated API Endpoints</h1><p>New content...</p>",
      "representation": "storage"
    }
  }
}
EOF
```

---

### Attachments

#### list-attachments

List attachments on a page.

**Usage:**

```bash
confluence-tool list-attachments <instance> <page_id> [limit]
```

**Example:**

```bash
confluence-tool list-attachments DEVERSIN "123456" 50
```

---

## Common Workflows

### Find and Update a Page

```bash
PAGES=$(confluence-tool search DEVERSIN 'type=page AND title="API Docs"' 1)
PAGE_ID=$(echo "$PAGES" | jq -r '.results[0].id')
VERSION=$(echo "$PAGES" | jq -r '.results[0].version.number')
NEXT_VERSION=$((VERSION + 1))

cat <<EOF | confluence-tool update-page DEVERSIN "$PAGE_ID" -
{
  "version": {"number": $NEXT_VERSION},
  "title": "API Documentation",
  "type": "page",
  "body": {
    "storage": {
      "value": "<p>Updated API docs...</p>",
      "representation": "storage"
    }
  }
}
EOF
```

### List All Pages in a Space

```bash
confluence-tool search DEVERSIN "type=page AND space=DEV" 100 | \
  jq -r '.results[] | "\(.id)\t\(.title)\t\(.version.when)"'
```

### Create Child Page

```bash
PARENT_ID="123456"

cat <<EOF | confluence-tool create-page DEVERSIN -
{
  "type": "page",
  "title": "Child Page",
  "space": {"key": "DEV"},
  "ancestors": [{"id": "$PARENT_ID"}],
  "body": {
    "storage": {
      "value": "<p>Child page content</p>",
      "representation": "storage"
    }
  }
}
EOF
```

---

## Environment Setup

Add to `~/.secrets`:

```bash
export CONFLUENCE_DEVERSIN_URL="https://confluence.deversin.com"
export CONFLUENCE_DEVERSIN_USERNAME="alexandr_kim"
export CONFLUENCE_DEVERSIN_PASSWORD="your_password"
export CONFLUENCE_DEVERSIN_BASIC_USER="internal"
export CONFLUENCE_DEVERSIN_BASIC_PASS="nginx_password"
```

Then source it:

```bash
source ~/.secrets
```

---

## CQL Reference

**Basic Syntax:**

```
field operator value
```

**Operators:**

- `=` - Equals
- `!=` - Not equals
- `~` - Contains
- `!~` - Does not contain
- `>` - Greater than
- `<` - Less than

**Logical:**

- `AND`
- `OR`
- `NOT`

**Common Fields:**

- `type` - Content type (page, blogpost, attachment)
- `space` - Space key
- `title` - Page title
- `text` - Page content
- `creator` - Creator username
- `contributor` - Contributor username
- `created` - Creation date
- `lastModified` - Last modification date

**Functions:**

- `currentUser()` - Current user
- `now()` - Current timestamp
- `startOfDay()` - Start of day
- `endOfDay()` - End of day

**Examples:**

```
type=page AND space=DEV
type=page AND creator=currentUser()
type=page AND lastModified > now("-7d")
text~"authentication" AND space in ("DEV", "PROD")
type=page AND title~"API" ORDER BY created DESC
```

---

For more details, see the [Confluence REST API documentation](https://docs.atlassian.com/atlassian-confluence/REST/latest/).
