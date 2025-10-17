#!/usr/bin/env python3

import sys
import subprocess
import json


def post_gitlab_comment(mr_number, comment):
    """Post comment to GitLab merge request."""
    try:
        # Use heredoc pattern to avoid escaping issues
        result = subprocess.run(
            ["glab", "mr", "note", mr_number, "-m", comment],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, f"Error posting to GitLab MR: {e.stderr}"
    except FileNotFoundError:
        return False, "Error: glab CLI not found. Install with: brew install glab"


def post_github_comment(pr_number, comment):
    """Post comment to GitHub pull request."""
    try:
        result = subprocess.run(
            ["gh", "pr", "comment", pr_number, "--body", comment],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, f"Error posting to GitHub PR: {e.stderr}"
    except FileNotFoundError:
        return False, "Error: gh CLI not found. Install with: brew install gh"


def main():
    if len(sys.argv) < 4:
        print("Usage: post_comment.py <platform> <issue_number> <comment>", file=sys.stderr)
        print("  platform: 'gitlab' or 'github'", file=sys.stderr)
        print("  issue_number: MR/PR number", file=sys.stderr)
        print("  comment: Comment text (use stdin with '-' for long comments)", file=sys.stderr)
        sys.exit(1)

    platform = sys.argv[1].lower()
    issue_number = sys.argv[2]

    # Support stdin for long comments
    if sys.argv[3] == "-":
        try:
            comment = sys.stdin.read()
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        comment = sys.argv[3]

    if not comment.strip():
        print("Error: Comment cannot be empty", file=sys.stderr)
        sys.exit(1)

    # Post comment based on platform
    if platform == "gitlab":
        success, message = post_gitlab_comment(issue_number, comment)
    elif platform == "github":
        success, message = post_github_comment(issue_number, comment)
    else:
        print(f"Error: Invalid platform '{platform}'. Use 'gitlab' or 'github'", file=sys.stderr)
        sys.exit(1)

    if success:
        print(f"✅ Comment posted successfully to {platform.title()} #{issue_number}")
        if message:
            print(message)
        sys.exit(0)
    else:
        print(message, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
