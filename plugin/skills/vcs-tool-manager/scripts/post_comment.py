#!/usr/bin/env python3

import sys
import subprocess
import json
import re
import os


def parse_gitlab_url(url):
    """Extract host, repo owner/name and MR number from GitLab URL."""
    match = re.match(r'https?://([^/]+)/([\w\-./]+?)/-/merge_requests/(\d+)', url)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None


def parse_github_url(url):
    """Extract repo owner/name and PR number from GitHub URL."""
    match = re.match(r'https?://github\.com/([^/]+/[^/]+)/pull/(\d+)', url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def post_gitlab_comment(mr_identifier, comment):
    """Post comment to GitLab merge request."""
    try:
        cmd = ["glab", "mr", "note"]
        env = None

        if mr_identifier.startswith('http'):
            host, repo, mr_number = parse_gitlab_url(mr_identifier)
            if not host or not repo or not mr_number:
                return False, f"Error: Could not parse GitLab URL: {mr_identifier}"

            if host.lower() != "gitlab.com":
                env = os.environ.copy()
                env["GITLAB_HOST"] = host

            cmd.extend(["--repo", repo, mr_number])
        else:
            cmd.append(mr_identifier)

        cmd.extend(["-m", comment])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, f"Error posting to GitLab MR: {e.stderr}"
    except FileNotFoundError:
        return False, "Error: glab CLI not found. Install with: brew install glab"


def post_github_comment(pr_identifier, comment):
    """Post comment to GitHub pull request."""
    try:
        cmd = ["gh", "pr", "comment"]

        if pr_identifier.startswith('http'):
            repo, pr_number = parse_github_url(pr_identifier)
            if not repo or not pr_number:
                return False, f"Error: Could not parse GitHub URL: {pr_identifier}"
            cmd.extend(["--repo", repo, pr_number])
        else:
            cmd.append(pr_identifier)

        cmd.extend(["--body", comment])

        result = subprocess.run(
            cmd,
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
        print("Usage: post_comment.py <platform> <url_or_number> <comment>", file=sys.stderr)
        print("  platform: 'gitlab' or 'github'", file=sys.stderr)
        print("  url_or_number: Full MR/PR URL or just the number (URL recommended)", file=sys.stderr)
        print("  comment: Comment text (use stdin with '-' for long comments)", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  post_comment.py gitlab https://gitlab.com/owner/repo/-/merge_requests/123 -", file=sys.stderr)
        print("  post_comment.py gitlab https://gitlab.example.com/owner/repo/-/merge_requests/456 -", file=sys.stderr)
        print("  post_comment.py github 789 'Short comment'", file=sys.stderr)
        sys.exit(1)

    platform = sys.argv[1].lower()
    url_or_number = sys.argv[2]

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
        success, message = post_gitlab_comment(url_or_number, comment)
    elif platform == "github":
        success, message = post_github_comment(url_or_number, comment)
    else:
        print(f"Error: Invalid platform '{platform}'. Use 'gitlab' or 'github'", file=sys.stderr)
        sys.exit(1)

    if success:
        identifier_display = url_or_number if not url_or_number.startswith('http') else f"MR/PR from {url_or_number}"
        print(f"✅ Comment posted successfully to {platform.title()}: {identifier_display}")
        if message:
            print(message)
        sys.exit(0)
    else:
        print(message, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
