# Jira Admin Scripts - Installation Guide

## Prerequisites

**Python 3** - Uses built-in `urllib`, no external packages required.

**Environment Variables** - Configured in `~/.secrets`:

```bash
export JIRA_<COMPANY>_URL="https://jira.example.com"
export JIRA_<COMPANY>_TOKEN="base64-encoded-userid:token"
```

## Generating API Tokens

### Jira Server/Data Center

For self-hosted Jira instances:

1. Go to your Jira instance (e.g., https://jira.deversin.com)
2. Click your profile icon → **Personal Access Tokens**
3. Click **Create token**
4. Give it a label (e.g., "Claude Code")
5. Copy the generated token

### Atlassian Cloud

1. Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Give it a label (e.g., "Claude Code")
4. Copy the token

### Encode for Bearer Auth

Jira Personal Access Tokens use Bearer Authentication with userid + token:

```bash
# For self-hosted Jira (userid from your profile):
echo -n "296979411732:your-pat-token" | base64

# For Atlassian Cloud (email + API token):
echo -n "your-email@example.com:your-api-token" | base64
```

Use the output as `JIRA_<COMPANY>_TOKEN`.

## Example Configuration

For company "4RA":

```bash
export JIRA_4RA_URL="https://jira.deversin.com"
export JIRA_4RA_TOKEN="$(echo -n '296979411732:abc123xyz' | base64)"
```

Add to `~/.secrets` and source:

```bash
source ~/.secrets
```

## Verification

Test the setup:

```bash
JIRA_TOOL=$(jq -r '."personal-marketplace".installLocation' ~/.claude/plugins/known_marketplaces.json)/plugin/skills/jira-admin/jira-tool.sh

"$JIRA_TOOL" discover
```

Should show your configured Jira instance(s).

## Common Issues

**"Error: JIRA_4RA_URL not set"**

- Make sure you've sourced `~/.secrets`: `source ~/.secrets`
- Check variable name matches pattern: `JIRA_<COMPANY>_URL`

**"HTTP 401 Unauthorized"**

- Token not base64 encoded correctly
- Token expired or revoked
- Wrong userid/token combination

**"HTTP 404 Not Found"**

- Wrong URL (check trailing slashes removed)
- Project/issue doesn't exist
- Insufficient permissions

## Script Structure

```
scripts/
├── jira_api.py              # Jira API wrapper class
├── discover.py              # Auto-discover Jira instances
├── jira_search_issues.py    # Search issues with JQL
├── jira_get_issue.py        # Get issue details
├── jira_create_issue.py     # Create issue
├── jira_update_issue.py     # Update issue
├── jira_list_sprints.py     # List sprints
└── jira_get_sprint.py       # Get sprint details
```

All scripts are standalone Python 3 files using only stdlib.

## API Documentation

- [Jira REST API v2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [JQL Reference](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)

## Authentication

This tool uses **Bearer token authentication** - no nginx basic auth required.

The token is sent as: `Authorization: Bearer <base64-token>`
