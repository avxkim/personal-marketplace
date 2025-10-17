#!/usr/bin/env python3

import sys
import json
import re
import os
from pathlib import Path

def find_line_numbers(file_path, pattern, context_hint=None, search_type="contains"):
    if not os.path.exists(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(json.dumps({"error": f"Failed to read file: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

    matches = []

    for line_num, line in enumerate(lines, start=1):
        line_stripped = line.strip()

        if search_type == "contains":
            if pattern in line:
                matches.append({
                    "line": line_num,
                    "content": line.rstrip(),
                    "context": get_context(lines, line_num - 1, 2)
                })
        elif search_type == "regex":
            if re.search(pattern, line):
                matches.append({
                    "line": line_num,
                    "content": line.rstrip(),
                    "context": get_context(lines, line_num - 1, 2)
                })

    if not matches:
        return {
            "found": False,
            "file": file_path,
            "pattern": pattern,
            "message": "No matches found"
        }

    if len(matches) == 1:
        return {
            "found": True,
            "file": file_path,
            "pattern": pattern,
            "line": matches[0]["line"],
            "content": matches[0]["content"],
            "context": matches[0]["context"],
            "match_count": 1
        }

    best_match = matches[0]
    if context_hint:
        for match in matches:
            context_str = "\n".join(match["context"])
            if context_hint.lower() in context_str.lower():
                best_match = match
                break

    return {
        "found": True,
        "file": file_path,
        "pattern": pattern,
        "line": best_match["line"],
        "content": best_match["content"],
        "context": best_match["context"],
        "match_count": len(matches),
        "all_matches": [{"line": m["line"], "content": m["content"]} for m in matches],
        "warning": f"Multiple matches found ({len(matches)}). Using best match based on context." if context_hint else f"Multiple matches found ({len(matches)}). Using first match."
    }

def get_context(lines, center_idx, radius=2):
    start = max(0, center_idx - radius)
    end = min(len(lines), center_idx + radius + 1)
    return [lines[i].rstrip() for i in range(start, end)]

def find_method_line(file_path, method_name):
    if not os.path.exists(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(json.dumps({"error": f"Failed to read file: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

    method_patterns = [
        rf'^\s*(public|private|protected)?\s*\w+\s+{re.escape(method_name)}\s*\(',
        rf'^\s*def\s+{re.escape(method_name)}\s*\(',
        rf'^\s*function\s+{re.escape(method_name)}\s*\(',
        rf'^\s*{re.escape(method_name)}\s*[:=]\s*function',
        rf'^\s*{re.escape(method_name)}\s*\(.*\)\s*{{',
        rf'^\s*func\s+{re.escape(method_name)}\s*\(',
    ]

    matches = []
    for line_num, line in enumerate(lines, start=1):
        for pattern in method_patterns:
            if re.search(pattern, line):
                matches.append({
                    "line": line_num,
                    "content": line.rstrip(),
                    "context": get_context(lines, line_num - 1, 3)
                })
                break

    if not matches:
        return {
            "found": False,
            "file": file_path,
            "method": method_name,
            "message": "Method not found"
        }

    match = matches[0]
    return {
        "found": True,
        "file": file_path,
        "method": method_name,
        "line": match["line"],
        "content": match["content"],
        "context": match["context"],
        "match_count": len(matches)
    }

def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: find_line_number.py <file_path> <pattern> [context_hint] [--method|--regex]"
        }), file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    pattern = sys.argv[2]
    context_hint = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None

    search_mode = "contains"
    if "--method" in sys.argv:
        result = find_method_line(file_path, pattern)
    elif "--regex" in sys.argv:
        search_mode = "regex"
        result = find_line_numbers(file_path, pattern, context_hint, search_mode)
    else:
        result = find_line_numbers(file_path, pattern, context_hint, search_mode)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("found", False) else 1)

if __name__ == "__main__":
    main()
