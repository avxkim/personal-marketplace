# VCS Tool Manager Scripts

Standalone Python utilities for GitLab and GitHub version control operations.

## Scripts

- `get_gitlab_mr_metadata.py` - Extract GitLab MR metadata
- `get_github_pr_metadata.py` - Extract GitHub PR metadata
- `format_blob_url.py` - Generate blob URLs with line numbers
- `validate_url.py` - Test URL accessibility via curl

## Key Features

### Automatic GITLAB_HOST Detection

The `get_gitlab_mr_metadata.py` script automatically:

1. Parses git remote URL to detect GitLab host
2. Sets `GITLAB_HOST` environment variable for self-hosted instances
3. Passes the environment to all `glab` commands

**No manual configuration needed** - works seamlessly with:

- gitlab.com (public GitLab)
- Self-hosted GitLab instances (auto-detected from git remote)

### Example

```bash
cd /path/to/gitlab-project

python3 get_gitlab_mr_metadata.py 123
```

The script automatically detects if remote is `gitlab.mycompany.com` and sets `GITLAB_HOST=gitlab.mycompany.com` before running `glab` commands.

## Usage

All scripts are designed as CLI tools:

```bash
python3 get_gitlab_mr_metadata.py <MR_NUMBER>
python3 get_github_pr_metadata.py <PR_NUMBER>
python3 format_blob_url.py '<JSON_METADATA>'
python3 validate_url.py <URL>
```

See parent `SKILL.md` for detailed documentation.
