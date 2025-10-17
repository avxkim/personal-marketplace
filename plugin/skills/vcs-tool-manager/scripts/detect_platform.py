#!/usr/bin/env python3

import subprocess
import sys
from typing import Optional


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def get_remote_url() -> Optional[str]:
    returncode, stdout, _ = run_command(["git", "remote", "get-url", "origin"])
    if returncode != 0:
        return None
    return stdout.strip()


def detect_platform(remote_url: str) -> Optional[str]:
    if not remote_url:
        return None

    remote_lower = remote_url.lower()

    if "github.com" in remote_lower:
        return "github"
    elif "gitlab" in remote_lower:
        return "gitlab"

    return None


def main():
    remote_url = get_remote_url()
    if not remote_url:
        print("Error: Could not get git remote URL", file=sys.stderr)
        sys.exit(1)

    platform = detect_platform(remote_url)
    if not platform:
        print(f"Error: Could not detect platform from remote URL: {remote_url}", file=sys.stderr)
        print("Supported platforms: github, gitlab", file=sys.stderr)
        sys.exit(1)

    print(platform)


if __name__ == "__main__":
    main()
