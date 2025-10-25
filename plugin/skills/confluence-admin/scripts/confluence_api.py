#!/usr/bin/env python3

import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Optional, Any
from confluence_auth import ConfluenceAuth


class ConfluenceAPI:
    def __init__(self, instance: str):
        self.auth = ConfluenceAuth(instance)
        self.base_url = self.auth.url
        self.opener = self.auth.get_opener()
        self.headers = self.auth.get_headers()

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

        req_data = None
        if data:
            req_data = json.dumps(data).encode('utf-8')

        request = urllib.request.Request(url, data=req_data, method=method)

        for key, value in self.headers.items():
            request.add_header(key, value)

        try:
            with self.opener.open(request, timeout=30) as response:
                response_text = response.read().decode('utf-8')
                if response_text:
                    return json.loads(response_text)
                return {}

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')

            if e.code == 401 and self.auth.auth_method == "nginx_browser":
                print("Session expired, clearing cache and retrying...", file=sys.stderr)
                self.auth.clear_cache()
                self.opener = self.auth.get_opener()

                request2 = urllib.request.Request(url, data=req_data, method=method)
                for key, value in self.headers.items():
                    request2.add_header(key, value)

                try:
                    with self.opener.open(request2, timeout=30) as response:
                        response_text = response.read().decode('utf-8')
                        if response_text:
                            return json.loads(response_text)
                        return {}
                except urllib.error.HTTPError as e2:
                    error_body2 = e2.read().decode('utf-8')
                    self._handle_error(e2.code, error_body2)
                except urllib.error.URLError as e2:
                    print(f"URL Error: {e2.reason}", file=sys.stderr)
                    sys.exit(1)
            else:
                self._handle_error(e.code, error_body)

        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}", file=sys.stderr)
            sys.exit(1)

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}", file=sys.stderr)
            sys.exit(1)

    def _handle_error(self, code: int, error_body: str):
        try:
            error_json = json.loads(error_body)
            if 'message' in error_json:
                print(f"Confluence Error ({code}): {error_json['message']}", file=sys.stderr)
            else:
                print(f"HTTP {code}: {error_body}", file=sys.stderr)
        except:
            print(f"HTTP {code}: {error_body}", file=sys.stderr)
        sys.exit(1)

    def get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return self._make_request(endpoint, "GET", params=params)

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request(endpoint, "POST", data=data)

    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request(endpoint, "PUT", data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        return self._make_request(endpoint, "DELETE")
