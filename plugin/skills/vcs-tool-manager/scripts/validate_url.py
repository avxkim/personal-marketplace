#!/usr/bin/env python3

import subprocess
import sys
from typing import Optional


def validate_url(url: str) -> tuple[bool, int, str]:
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
            capture_output=True,
            text=True,
            timeout=10
        )

        status_code = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0

        is_valid = status_code in [200, 302]
        message = "Valid" if is_valid else f"Invalid (HTTP {status_code})"

        return is_valid, status_code, message

    except subprocess.TimeoutExpired:
        return False, 0, "Timeout"
    except Exception as e:
        return False, 0, f"Error: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_url.py <URL>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    is_valid, status_code, message = validate_url(url)

    result = {
        "url": url,
        "valid": is_valid,
        "status_code": status_code,
        "message": message
    }

    print(f"URL: {url}")
    print(f"Status: {message}")
    print(f"HTTP Code: {status_code}")

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
