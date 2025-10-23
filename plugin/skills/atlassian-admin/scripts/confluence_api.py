#!/usr/bin/env python3

import os
import sys
import json
import base64
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Optional, Any


class ConfluenceAPI:
    def __init__(self, instance: str):
        url_var = f"CONFLUENCE_{instance.upper()}_URL"
        token_var = f"CONFLUENCE_{instance.upper()}_TOKEN"

        self.base_url = os.getenv(url_var)
        self.token = os.getenv(token_var)

        if not self.base_url:
            print(f"Error: {url_var} not set", file=sys.stderr)
            print("Hint: Run 'discover' to see available instances", file=sys.stderr)
            sys.exit(1)

        if not self.token:
            print(f"Error: {token_var} not set", file=sys.stderr)
            print("Hint: Source ~/.secrets file", file=sys.stderr)
            sys.exit(1)

        self.base_url = self.base_url.rstrip('/')

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api/{endpoint.lstrip('/')}"

        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        headers = {
            "Authorization": f"Basic {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        req_data = None
        if data:
            req_data = json.dumps(data).encode('utf-8')

        request = urllib.request.Request(url, data=req_data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(request) as response:
                response_text = response.read().decode('utf-8')
                if response_text:
                    return json.loads(response_text)
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_json = json.loads(error_body)
                if 'message' in error_json:
                    print(f"Confluence Error: {error_json['message']}", file=sys.stderr)
                else:
                    print(f"HTTP {e.code}: {error_body}", file=sys.stderr)
            except:
                print(f"HTTP {e.code}: {error_body}", file=sys.stderr)
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
