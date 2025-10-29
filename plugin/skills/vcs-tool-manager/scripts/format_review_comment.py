#!/usr/bin/env python3

import json
import sys
from typing import List, Dict, Optional


def format_code_review(data: Dict) -> str:
    """Format code review comment."""
    lines = ["# Code Review Summary 🔍\n"]

    # Critical Issues
    critical = data.get("critical", [])
    if critical:
        lines.append("## 🔴 Critical Issues (Must Fix)\n")
        for idx, issue in enumerate(critical, 1):
            file_path = issue.get("file", "Unknown")
            line = issue.get("line")
            url = issue.get("url", "")
            desc = issue.get("description") or issue.get("message", "")

            # Extract just the filename from full path
            filename = file_path.split("/")[-1] if "/" in file_path else file_path

            if line and url:
                lines.append(f'{idx}. <big>**{filename}**</big> ([{file_path}:{line}]({url})):')
            else:
                lines.append(f'{idx}. <big>**{filename}**</big> ({file_path}):')

            lines.append(f'   {desc}\n')

        lines.append("---\n")

    # Warnings
    warnings = data.get("warnings", [])
    if warnings:
        lines.append("## 🟡 Warnings (Should Fix)\n")
        for idx, issue in enumerate(warnings, 1):
            file_path = issue.get("file", "Unknown")
            line = issue.get("line")
            url = issue.get("url", "")
            desc = issue.get("description") or issue.get("message", "")

            # Extract just the filename from full path
            filename = file_path.split("/")[-1] if "/" in file_path else file_path

            if line and url:
                lines.append(f'{idx}. <big>**{filename}**</big> ([{file_path}:{line}]({url})):')
            else:
                lines.append(f'{idx}. <big>**{filename}**</big> ({file_path}):')

            lines.append(f'   {desc}\n')

        lines.append("---\n")

    # Suggestions
    suggestions = data.get("suggestions", [])
    if suggestions:
        lines.append("## 🟢 Suggestions (Consider)\n")
        for idx, issue in enumerate(suggestions, 1):
            file_path = issue.get("file", "Unknown")
            line = issue.get("line")
            url = issue.get("url", "")
            desc = issue.get("description") or issue.get("message", "")

            # Extract just the filename from full path
            filename = file_path.split("/")[-1] if "/" in file_path else file_path

            if line and url:
                lines.append(f'{idx}. <big>**{filename}**</big> ([{file_path}:{line}]({url})):')
            else:
                lines.append(f'{idx}. <big>**{filename}**</big> ({file_path}):')

            lines.append(f'   {desc}\n')

        lines.append("---\n")

    # Verdict
    lines.append("## ⚖️ Verdict\n")
    verdict = data.get("verdict", "").upper()
    if verdict == "PASS":
        lines.append("**PASS** ✔️ - Ready for merge\n")
    elif verdict == "FAIL":
        lines.append("**FAIL** ❌ - Requires fixes before merge\n")
    else:
        lines.append(f"**{verdict}**\n")

    return "\n".join(lines)


def format_architecture_review(data: Dict) -> str:
    """Format architecture review comment."""
    lines = ["# Architecture Assessment 🏗️\n"]

    concerns = data.get("concerns", [])

    critical = [c for c in concerns if c.get("severity", "").lower() == "critical"]
    major = [c for c in concerns if c.get("severity", "").lower() == "major"]
    minor = [c for c in concerns if c.get("severity", "").lower() == "minor"]

    if critical:
        lines.append("## 🔴 Critical Concerns (Must Address)\n")
        for idx, concern in enumerate(critical, 1):
            file_path = concern.get("file")
            line = concern.get("line")
            url = concern.get("url", "")
            desc = concern.get("description") or concern.get("message", "")

            if file_path:
                filename = file_path.split("/")[-1] if "/" in file_path else file_path
                if line and url:
                    lines.append(f'{idx}. <big>**{filename}**</big> ([{file_path}:{line}]({url})):')
                else:
                    lines.append(f'{idx}. <big>**{filename}**</big> ({file_path}):')
            else:
                lines.append(f'{idx}. **Critical**:')

            lines.append(f'   {desc}\n')

        lines.append("---\n")

    if major:
        lines.append("## 🟠 Major Concerns (Should Address)\n")
        for idx, concern in enumerate(major, 1):
            file_path = concern.get("file")
            line = concern.get("line")
            url = concern.get("url", "")
            desc = concern.get("description") or concern.get("message", "")

            if file_path:
                filename = file_path.split("/")[-1] if "/" in file_path else file_path
                if line and url:
                    lines.append(f'{idx}. <big>**{filename}**</big> ([{file_path}:{line}]({url})):')
                else:
                    lines.append(f'{idx}. <big>**{filename}**</big> ({file_path}):')
            else:
                lines.append(f'{idx}. **Major**:')

            lines.append(f'   {desc}\n')

        lines.append("---\n")

    if minor:
        lines.append("## 🟡 Minor Concerns (Consider)\n")
        for idx, concern in enumerate(minor, 1):
            file_path = concern.get("file")
            line = concern.get("line")
            url = concern.get("url", "")
            desc = concern.get("description") or concern.get("message", "")

            if file_path:
                filename = file_path.split("/")[-1] if "/" in file_path else file_path
                if line and url:
                    lines.append(f'{idx}. <big>**{filename}**</big> ([{file_path}:{line}]({url})):')
                else:
                    lines.append(f'{idx}. <big>**{filename}**</big> ({file_path}):')
            else:
                lines.append(f'{idx}. **Minor**:')

            lines.append(f'   {desc}\n')

        lines.append("---\n")

    return "\n".join(lines)


def main():
    # Read JSON from stdin if no arguments, otherwise from argument
    if len(sys.argv) < 2 or sys.argv[1] == "-":
        try:
            json_input = sys.stdin.read()
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        json_input = sys.argv[1]

    try:
        data = json.loads(json_input)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    review_type = data.get("type", "").lower()

    if review_type == "code":
        output = format_code_review(data)
        print(output)
    elif review_type == "architecture":
        output = format_architecture_review(data)
        print(output)
    else:
        print(f"Error: Invalid type '{review_type}'. Use 'code' or 'architecture'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
