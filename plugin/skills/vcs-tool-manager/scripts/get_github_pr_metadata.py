#!/usr/bin/env python3

import json
import subprocess
import sys
from typing import Dict, Optional


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def get_remote_url() -> Optional[str]:
    returncode, stdout, _ = run_command(["git", "remote", "get-url", "origin"])
    if returncode != 0:
        return None
    return stdout.strip()


def parse_github_url(remote_url: str) -> tuple[Optional[str], Optional[str]]:
    if not remote_url:
        return None, None

    url = remote_url.replace("git@github.com:", "https://github.com/").replace(".git", "")

    if "github.com/" in url:
        parts = url.split("github.com/")
        if len(parts) != 2:
            return None, None

        path_parts = parts[1].split("/")
        if len(path_parts) < 2:
            return None, None

        owner = path_parts[0]
        repo = path_parts[1]
        return owner, repo

    return None, None


def get_pr_metadata(pr_number: str) -> Optional[Dict[str, str]]:
    returncode, stdout, stderr = run_command([
        "gh", "pr", "view", pr_number, "--json", "headRefName,headRefOid,url"
    ])

    if returncode != 0:
        print(f"Error running gh pr view: {stderr}", file=sys.stderr)
        return None

    try:
        data = json.loads(stdout)
        return {
            "head_ref": data.get("headRefName", ""),
            "sha": data.get("headRefOid", ""),
            "web_url": data.get("url", "")
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: get_github_pr_metadata.py <PR_NUMBER>", file=sys.stderr)
        sys.exit(1)

    pr_number = sys.argv[1]

    remote_url = get_remote_url()
    if not remote_url:
        print("Error: Could not get git remote URL", file=sys.stderr)
        sys.exit(1)

    owner, repo = parse_github_url(remote_url)
    if not all([owner, repo]):
        print(f"Error: Could not parse GitHub URL from: {remote_url}", file=sys.stderr)
        sys.exit(1)

    metadata = get_pr_metadata(pr_number)

    if not metadata:
        print("Error: Could not retrieve PR metadata", file=sys.stderr)
        sys.exit(1)

    result = {
        "owner": owner,
        "repo": repo,
        "head_ref": metadata["head_ref"],
        "sha": metadata["sha"],
        "web_url": metadata["web_url"]
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
