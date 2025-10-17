#!/usr/bin/env python3

import json
import sys
from typing import Optional
from urllib.parse import quote


def format_gitlab_url(
    host: str,
    namespace: str,
    repo: str,
    file_path: str,
    line_number: int,
    sha: str,
    branch: str
) -> str:
    encoded_path = quote(file_path, safe="/")

    url = f"https://{host}/{namespace}/{repo}/-/blob/{sha}/{encoded_path}"

    if line_number > 0:
        url += f"#L{line_number}"

    return url


def format_github_url(
    owner: str,
    repo: str,
    file_path: str,
    line_number: int,
    sha: str,
    branch: str
) -> str:
    encoded_path = quote(file_path, safe="/")

    url = f"https://github.com/{owner}/{repo}/blob/{sha}/{encoded_path}"

    if line_number > 0:
        url += f"#L{line_number}"

    return url


def main():
    if len(sys.argv) < 2:
        print("Usage: format_blob_url.py <JSON_METADATA>", file=sys.stderr)
        print("JSON should contain: platform, file_path, line_number, and platform-specific fields", file=sys.stderr)
        sys.exit(1)

    try:
        metadata = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    platform = metadata.get("platform", "").lower()
    file_path = metadata.get("file_path", "")
    line_number = metadata.get("line_number", 0)

    if not file_path:
        print("Error: file_path is required", file=sys.stderr)
        sys.exit(1)

    if platform == "gitlab":
        host = metadata.get("host", "")
        namespace = metadata.get("namespace", "")
        repo = metadata.get("repo", "")
        sha = metadata.get("sha", "")
        branch = metadata.get("source_branch", "")

        if not all([host, namespace, repo, sha]):
            print("Error: GitLab requires host, namespace, repo, sha", file=sys.stderr)
            sys.exit(1)

        url = format_gitlab_url(host, namespace, repo, file_path, line_number, sha, branch)
        print(url)

    elif platform == "github":
        owner = metadata.get("owner", "")
        repo = metadata.get("repo", "")
        sha = metadata.get("sha", "")
        branch = metadata.get("head_ref", "")

        if not all([owner, repo, sha]):
            print("Error: GitHub requires owner, repo, sha", file=sys.stderr)
            sys.exit(1)

        url = format_github_url(owner, repo, file_path, line_number, sha, branch)
        print(url)

    else:
        print(f"Error: Unsupported platform '{platform}'. Use 'gitlab' or 'github'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
