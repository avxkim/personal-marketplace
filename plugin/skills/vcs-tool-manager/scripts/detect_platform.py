#!/usr/bin/env python3

import subprocess
import sys
import os
import re
import argparse
from typing import Optional


def run_command(cmd: list[str], cwd: Optional[str] = None) -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr


def get_remote_url(repo_dir: Optional[str] = None) -> Optional[str]:
    returncode, stdout, _ = run_command(["git", "remote", "get-url", "origin"], cwd=repo_dir)
    if returncode != 0:
        return None
    return stdout.strip()


def detect_platform_from_url(url: str) -> Optional[str]:
    if not url:
        return None

    url_lower = url.lower()

    if "github.com" in url_lower:
        return "github"
    elif "gitlab" in url_lower:
        return "gitlab"

    return None


def extract_repo_from_url(url: str) -> Optional[str]:
    gitlab_match = re.match(r'https?://[^/]+/([\w\-./]+?)/-/merge_requests/\d+', url)
    if gitlab_match:
        return gitlab_match.group(1)

    github_match = re.match(r'https?://github\.com/([^/]+/[^/]+)/pull/\d+', url)
    if github_match:
        return github_match.group(1)

    return None


def find_repo_root(target_repo: str, search_from: str) -> Optional[str]:
    current = os.path.abspath(search_from)

    while True:
        git_dir = os.path.join(current, '.git')
        if os.path.isdir(git_dir):
            remote_url = get_remote_url(current)
            if remote_url and target_repo in remote_url:
                return current

        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    return None


def main():
    parser = argparse.ArgumentParser(description='Detect VCS platform (GitHub or GitLab)')
    parser.add_argument('--url', help='MR/PR URL to extract platform from')
    parser.add_argument('--repo-dir', help='Repository directory to check (default: current directory)')
    parser.add_argument('--debug', action='store_true', help='Show debug information')

    args = parser.parse_args()

    repo_dir = args.repo_dir or os.getcwd()

    if args.debug:
        print(f"[DEBUG] Current working directory: {os.getcwd()}", file=sys.stderr)
        print(f"[DEBUG] Target repo directory: {repo_dir}", file=sys.stderr)
        if args.url:
            print(f"[DEBUG] URL provided: {args.url}", file=sys.stderr)

    if args.url:
        platform = detect_platform_from_url(args.url)
        if platform:
            if args.debug:
                print(f"[DEBUG] Platform detected from URL: {platform}", file=sys.stderr)
            print(platform)
            return

        target_repo = extract_repo_from_url(args.url)
        if target_repo:
            if args.debug:
                print(f"[DEBUG] Extracted repo from URL: {target_repo}", file=sys.stderr)

            found_dir = find_repo_root(target_repo, repo_dir)
            if found_dir:
                if args.debug:
                    print(f"[DEBUG] Found matching repo at: {found_dir}", file=sys.stderr)
                repo_dir = found_dir

    remote_url = get_remote_url(repo_dir)
    if not remote_url:
        print(f"Error: Could not get git remote URL from {repo_dir}", file=sys.stderr)
        if args.debug:
            returncode, stdout, stderr = run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_dir)
            print(f"[DEBUG] Is git repo: {returncode == 0}", file=sys.stderr)
        sys.exit(1)

    if args.debug:
        print(f"[DEBUG] Remote URL: {remote_url}", file=sys.stderr)

    platform = detect_platform_from_url(remote_url)
    if not platform:
        print(f"Error: Could not detect platform from remote URL: {remote_url}", file=sys.stderr)
        print("Supported platforms: github, gitlab", file=sys.stderr)
        sys.exit(1)

    if args.debug:
        print(f"[DEBUG] Platform detected: {platform}", file=sys.stderr)

    print(platform)


if __name__ == "__main__":
    main()
