#!/usr/bin/env python3

import subprocess
import sys
import re
import os
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip(), result.returncode

def detect_platform(cwd=None):
    remote_url, _ = run_command("git remote get-url origin", cwd=cwd)
    if "github.com" in remote_url:
        return "github"
    elif "gitlab" in remote_url:
        return "gitlab"
    else:
        print("Error: Unable to detect platform (GitHub or GitLab)", file=sys.stderr)
        sys.exit(1)

def get_current_branch(cwd=None):
    branch, _ = run_command("git branch --show-current", cwd=cwd)
    return branch

def get_default_branch(platform, cwd=None):
    if platform == "github":
        default_branch, code = run_command("gh repo view --json defaultBranchRef --jq .defaultBranchRef.name", cwd=cwd, check=False)
        if code == 0 and default_branch:
            return default_branch
    elif platform == "gitlab":
        default_branch, code = run_command("glab repo view --json default_branch --jq .default_branch", cwd=cwd, check=False)
        if code == 0 and default_branch:
            return default_branch

    for branch in ["main", "master", "develop"]:
        _, code = run_command(f"git rev-parse --verify {branch}", cwd=cwd, check=False)
        if code == 0:
            return branch

    return "main"

def extract_task_id(branch_name):
    patterns = [
        r'([A-Z]+-\d+)',
        r'([A-Z]{2,}\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, branch_name, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None

def generate_title(branch_name, task_id):
    if task_id:
        clean_name = re.sub(r'[A-Z]+-\d+[_-]?', '', branch_name, flags=re.IGNORECASE)
        clean_name = clean_name.replace('_', ' ').replace('-', ' ').strip()
        return f"{task_id}: {clean_name}"

    prefixes = ['feat', 'fix', 'chore', 'refactor', 'docs', 'test', 'style', 'perf']
    for prefix in prefixes:
        if branch_name.startswith(f"{prefix}/") or branch_name.startswith(f"{prefix}-"):
            clean_name = branch_name[len(prefix)+1:].replace('_', ' ').replace('-', ' ').strip()
            return f"{prefix}: {clean_name}"

    clean_name = branch_name.replace('_', ' ').replace('-', ' ').strip()
    return f"feat: {clean_name}"

def generate_description(task_id):
    if task_id:
        return f"Closes: {task_id}"
    return ""

def find_nested_repos(root_path):
    nested_repos = []
    root_git = Path(root_path) / ".git"

    for item in Path(root_path).rglob(".git"):
        if item.is_dir() and item != root_git:
            repo_path = item.parent
            nested_repos.append(str(repo_path))

    return nested_repos

def has_changes(repo_path):
    _, code = run_command("git diff --quiet HEAD", cwd=repo_path, check=False)
    if code != 0:
        return True

    status, _ = run_command("git status --porcelain", cwd=repo_path)
    return bool(status.strip())

def get_cli_help(platform):
    if platform == "github":
        help_output, _ = run_command("gh pr create --help")
        return help_output
    else:
        help_output, _ = run_command("glab mr create --help")
        return help_output

def create_pr_mr(platform, source, target, title, description, assignee=None, cwd=None):
    if platform == "github":
        cmd = f'gh pr create --base {target} --head {source} --title "{title}"'
        if description:
            cmd += f' --body "$(cat <<\'EOF\'\n{description}\nEOF\n)"'
        if assignee:
            cmd += f' --assignee {assignee}'
    else:
        cmd = f'glab mr create --source-branch {source} --target-branch {target} --title "{title}"'
        if description:
            cmd += f' --description "$(cat <<\'EOF\'\n{description}\nEOF\n)"'
        if assignee:
            cmd += f' --assignee {assignee}'

    print(f"\n{'='*60}")
    print(f"Creating {'PR' if platform == 'github' else 'MR'} in: {cwd or 'current directory'}")
    print(f"Source: {source} -> Target: {target}")
    print(f"Title: {title}")
    print(f"{'='*60}\n")

    output, code = run_command(cmd, cwd=cwd, check=False)
    if code == 0:
        print(output)
        print(f"\n✓ {'PR' if platform == 'github' else 'MR'} created successfully!")
    else:
        print(f"✗ Failed to create {'PR' if platform == 'github' else 'MR'}", file=sys.stderr)

    return code == 0

def main():
    args = sys.argv[1:]

    root_path = run_command("git rev-parse --show-toplevel")[0]
    platform = detect_platform()
    current_branch = get_current_branch()
    default_branch = get_default_branch(platform)

    source = current_branch
    target = default_branch
    assignee = None

    if len(args) == 1:
        target = args[0]
    elif len(args) == 2:
        source = args[0]
        target = args[1]
    elif len(args) >= 3:
        source = args[0]
        target = args[1]
        assignee = args[2]

    task_id = extract_task_id(source)
    title = generate_title(source, task_id)
    description = generate_description(task_id)

    print(f"\nPlatform: {platform.upper()}")
    print(f"Current branch: {current_branch}")
    print(f"Default branch: {default_branch}")

    if task_id:
        print(f"Task ID detected: {task_id}")

    print(f"\nChecking CLI version...")
    get_cli_help(platform)

    success = create_pr_mr(platform, source, target, title, description, assignee, root_path)

    nested_repos = find_nested_repos(root_path)
    if nested_repos:
        print(f"\n{'='*60}")
        print(f"Found {len(nested_repos)} nested repository(ies):")
        print(f"{'='*60}")

        for nested_repo in nested_repos:
            print(f"\n→ Checking: {nested_repo}")

            if has_changes(nested_repo):
                nested_platform = detect_platform(nested_repo)
                nested_branch = get_current_branch(nested_repo)
                nested_default = get_default_branch(nested_platform, nested_repo)
                nested_task_id = extract_task_id(nested_branch)
                nested_title = generate_title(nested_branch, nested_task_id)
                nested_description = generate_description(nested_task_id)

                create_pr_mr(
                    nested_platform,
                    nested_branch,
                    nested_default,
                    nested_title,
                    nested_description,
                    assignee,
                    nested_repo
                )
            else:
                print(f"  No changes detected, skipping...")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
