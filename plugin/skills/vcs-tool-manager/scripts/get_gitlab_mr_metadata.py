#!/usr/bin/env python3

import json
import os
import subprocess
import sys
from typing import Dict, Optional
from urllib.parse import quote


def run_command(cmd: list[str], env: Optional[Dict[str, str]] = None) -> tuple[int, str, str]:
    command_env = os.environ.copy()
    if env:
        command_env.update(env)
    result = subprocess.run(cmd, capture_output=True, text=True, env=command_env)
    return result.returncode, result.stdout, result.stderr


def get_remote_url() -> Optional[str]:
    returncode, stdout, _ = run_command(["git", "remote", "get-url", "origin"])
    if returncode != 0:
        return None
    return stdout.strip()


def parse_gitlab_url(remote_url: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    if not remote_url:
        return None, None, None

    url = remote_url.replace("git@", "https://").replace(".git", "")

    if "://" in url:
        parts = url.split("://")
        if len(parts) != 2:
            return None, None, None
        protocol, rest = parts
        host_and_path = rest.replace(":", "/")
    else:
        return None, None, None

    path_parts = host_and_path.split("/")
    if len(path_parts) < 3:
        return None, None, None

    host = path_parts[0]
    namespace = path_parts[1]
    repo = path_parts[2]

    return host, namespace, repo


def get_mr_metadata_via_view(mr_number: str, gitlab_env: Dict[str, str]) -> Optional[Dict[str, str]]:
    returncode, stdout, stderr = run_command([
        "glab", "mr", "view", mr_number, "--output", "json"
    ], env=gitlab_env)

    if returncode != 0:
        print(f"Error running glab mr view: {stderr}", file=sys.stderr)
        return None

    try:
        data = json.loads(stdout)
        return {
            "source_branch": data.get("source_branch", ""),
            "sha": data.get("sha", ""),
            "web_url": data.get("web_url", "")
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return None


def get_mr_metadata_via_api(mr_number: str, namespace: str, repo: str, gitlab_env: Dict[str, str]) -> Optional[Dict[str, str]]:
    project_path = quote(f"{namespace}/{repo}", safe="")
    returncode, stdout, stderr = run_command([
        "glab", "api", f"projects/{project_path}/merge_requests/{mr_number}"
    ], env=gitlab_env)

    if returncode != 0:
        print(f"Error running glab api: {stderr}", file=sys.stderr)
        return None

    try:
        data = json.loads(stdout)
        return {
            "source_branch": data.get("source_branch", ""),
            "sha": data.get("sha", ""),
            "web_url": data.get("web_url", "")
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: get_gitlab_mr_metadata.py <MR_NUMBER>", file=sys.stderr)
        sys.exit(1)

    mr_number = sys.argv[1]

    remote_url = get_remote_url()
    if not remote_url:
        print("Error: Could not get git remote URL", file=sys.stderr)
        sys.exit(1)

    host, namespace, repo = parse_gitlab_url(remote_url)
    if not all([host, namespace, repo]):
        print(f"Error: Could not parse GitLab URL from: {remote_url}", file=sys.stderr)
        sys.exit(1)

    gitlab_env = {}
    if host and host.lower() != "gitlab.com":
        gitlab_env["GITLAB_HOST"] = host

    metadata = get_mr_metadata_via_view(mr_number, gitlab_env)

    if not metadata:
        metadata = get_mr_metadata_via_api(mr_number, namespace, repo, gitlab_env)

    if not metadata:
        print("Error: Could not retrieve MR metadata", file=sys.stderr)
        sys.exit(1)

    result = {
        "host": host,
        "namespace": namespace,
        "repo": repo,
        "source_branch": metadata["source_branch"],
        "sha": metadata["sha"],
        "web_url": metadata["web_url"]
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
