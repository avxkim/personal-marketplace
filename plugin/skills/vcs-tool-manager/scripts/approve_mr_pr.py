#!/usr/bin/env python3

import sys
import subprocess
import re
import os


def parse_gitlab_url(url):
    match = re.match(r'https?://([^/]+)/([\w\-./]+?)/-/merge_requests/(\d+)', url)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None


def parse_github_url(url):
    match = re.match(r'https?://github\.com/([^/]+/[^/]+)/pull/(\d+)', url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def verify_gitlab_syntax():
    try:
        result = subprocess.run(
            ["glab", "mr", "approve", "--help"],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error checking glab syntax: {e.stderr}"
    except FileNotFoundError:
        return False, "Error: glab CLI not found. Install with: brew install glab"


def verify_github_syntax():
    try:
        result = subprocess.run(
            ["gh", "pr", "review", "--help"],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error checking gh syntax: {e.stderr}"
    except FileNotFoundError:
        return False, "Error: gh CLI not found. Install with: brew install gh"


def approve_gitlab_mr(mr_identifier):
    success, help_output = verify_gitlab_syntax()
    if not success:
        return False, help_output

    try:
        cmd = ["glab", "mr", "approve"]
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

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, f"Error approving GitLab MR: {e.stderr}"


def approve_github_pr(pr_identifier):
    success, help_output = verify_github_syntax()
    if not success:
        return False, help_output

    try:
        cmd = ["gh", "pr", "review", "--approve"]

        if pr_identifier.startswith('http'):
            repo, pr_number = parse_github_url(pr_identifier)
            if not repo or not pr_number:
                return False, f"Error: Could not parse GitHub URL: {pr_identifier}"
            cmd.extend(["--repo", repo, pr_number])
        else:
            cmd.append(pr_identifier)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, f"Error approving GitHub PR: {e.stderr}"


def main():
    if len(sys.argv) < 3:
        print("Usage: approve_mr_pr.py <platform> <url_or_number>", file=sys.stderr)
        print("  platform: 'gitlab' or 'github'", file=sys.stderr)
        print("  url_or_number: Full MR/PR URL or just the number (URL recommended)", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  approve_mr_pr.py gitlab https://gitlab.com/owner/repo/-/merge_requests/123", file=sys.stderr)
        print("  approve_mr_pr.py gitlab https://gitlab.example.com/owner/repo/-/merge_requests/456", file=sys.stderr)
        print("  approve_mr_pr.py github https://github.com/owner/repo/pull/789", file=sys.stderr)
        print("  approve_mr_pr.py github 789", file=sys.stderr)
        sys.exit(1)

    platform = sys.argv[1].lower()
    url_or_number = sys.argv[2]

    if platform == "gitlab":
        success, message = approve_gitlab_mr(url_or_number)
    elif platform == "github":
        success, message = approve_github_pr(url_or_number)
    else:
        print(f"Error: Invalid platform '{platform}'. Use 'gitlab' or 'github'", file=sys.stderr)
        sys.exit(1)

    if success:
        identifier_display = url_or_number if not url_or_number.startswith('http') else f"MR/PR from {url_or_number}"
        print(f"✅ MR/PR approved successfully on {platform.title()}: {identifier_display}")
        if message:
            print(message)
        sys.exit(0)
    else:
        print(message, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
