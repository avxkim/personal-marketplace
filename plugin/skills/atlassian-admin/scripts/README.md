# Atlassian Admin Scripts - Installation Guide

## Prerequisites

**Python 3** - Uses built-in `urllib`, no external packages required.

**Environment Variables** - Configured in `~/.secrets`:

```bash
export JIRA_<COMPANY>_URL="https://jira.example.com"
export JIRA_<COMPANY>_TOKEN="base64-encoded-token"
export CONFLUENCE_<COMPANY>_URL="https://confluence.example.com"
export CONFLUENCE_<COMPANY>_TOKEN="base64-encoded-token"
```

## Generating API Tokens

### Atlassian Cloud

1. Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Give it a label (e.g., "Claude Code")
4. Copy the token

### Encode for Basic Auth

Atlassian REST APIs use Basic Authentication with email + token:

```bash
echo -n "your-email@example.com:your-api-token" | base64
```

Use the output as `JIRA_<COMPANY>_TOKEN` or `CONFLUENCE_<COMPANY>_TOKEN`.

## Example Configuration

For company "4RA":

```bash
export JIRA_4RA_URL="https://jira.deversin.com"
export JIRA_4RA_TOKEN="$(echo -n 'alex@example.com:abc123xyz' | base64)"
export CONFLUENCE_4RA_URL="https://confluence.deversin.com"
export CONFLUENCE_4RA_TOKEN="$(echo -n 'alex@example.com:def456uvw' | base64)"
```

Add to `~/.secrets` and source:

```bash
source ~/.secrets
```

## Verification

Test the setup:

```bash
ATLASSIAN_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/atlassian-admin/atlassian-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)

"$ATLASSIAN_TOOL" discover
```

Should show your configured instances.

## Common Issues

**"Error: JIRA_4RA_URL not set"**

- Make sure you've sourced `~/.secrets`: `source ~/.secrets`
- Check variable name matches pattern: `JIRA_<COMPANY>_URL`

**"HTTP 401 Unauthorized"**

- Token not base64 encoded correctly
- Token expired or revoked
- Wrong email/token combination

**"HTTP 404 Not Found"**

- Wrong URL (check trailing slashes removed)
- Project/space doesn't exist
- Insufficient permissions

## Script Structure

```
scripts/
├── jira_api.py              # Jira API wrapper class
├── confluence_api.py        # Confluence API wrapper class
├── discover.py              # Auto-discover instances
├── jira_search_issues.py    # Search issues with JQL
├── jira_get_issue.py        # Get issue details
├── jira_create_issue.py     # Create issue
├── jira_update_issue.py     # Update issue
├── jira_list_sprints.py     # List sprints
├── jira_get_sprint.py       # Get sprint details
├── confluence_get_page.py   # Get page by URL/ID/space+title
├── confluence_search.py     # Search with CQL
├── confluence_create_page.py # Create page
├── confluence_update_page.py # Update page
├── confluence_list_spaces.py # List spaces
└── confluence_list_pages.py  # List pages in space
```

All scripts are standalone Python 3 files using only stdlib.

## API Documentation

- [Jira REST API v2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/)
- [JQL Reference](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
- [CQL Reference](https://developer.atlassian.com/server/confluence/advanced-searching-using-cql/)
