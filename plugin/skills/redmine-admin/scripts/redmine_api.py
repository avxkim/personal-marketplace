#!/usr/bin/env python3

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Optional, Any

REDMINE_COMMENT_MAX_LENGTH = 10000


class RedmineAPI:
    def __init__(self):
        self.api_key = os.getenv("REDMINE_API_KEY")
        self.base_url = os.getenv("REDMINE_URL")

        if not self.api_key:
            print("Error: REDMINE_API_KEY environment variable not set", file=sys.stderr)
            print("Hint: Source credentials from ~/.secrets file", file=sys.stderr)
            sys.exit(1)

        if not self.base_url:
            print("Error: REDMINE_URL environment variable not set", file=sys.stderr)
            print("Hint: Source credentials from ~/.secrets file", file=sys.stderr)
            sys.exit(1)

        self.base_url = self.base_url.rstrip('/')

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        headers = {
            "X-Redmine-API-Key": self.api_key,
            "Content-Type": "application/json; charset=utf-8"
        }

        req_data = None
        if data:
            req_data = json.dumps(data, ensure_ascii=False).encode('utf-8')

        request = urllib.request.Request(url, data=req_data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(request) as response:
                response_text = response.read().decode('utf-8')
                if response_text:
                    return json.loads(response_text)
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}", file=sys.stderr)
            sys.exit(1)

    def get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return self._make_request(endpoint, "GET", params=params)

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request(endpoint, "POST", data=data)

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request(endpoint, "PUT", data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        return self._make_request(endpoint, "DELETE")
