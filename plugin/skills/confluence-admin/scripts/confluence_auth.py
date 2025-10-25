#!/usr/bin/env python3

import os
import sys
import json
import base64
import time
import urllib.request
import urllib.error
from http.cookiejar import Cookie, CookieJar
from typing import Optional, Dict, Any


class ConfluenceAuth:
    def __init__(self, instance: str):
        self.instance = instance.upper()
        self.url = os.getenv(f"CONFLUENCE_{self.instance}_URL")
        self.username = os.getenv(f"CONFLUENCE_{self.instance}_USERNAME")
        self.password = os.getenv(f"CONFLUENCE_{self.instance}_PASSWORD")
        self.pat = os.getenv(f"CONFLUENCE_{self.instance}_PAT")
        self.basic_user = os.getenv(f"CONFLUENCE_{self.instance}_BASIC_USER")
        self.basic_pass = os.getenv(f"CONFLUENCE_{self.instance}_BASIC_PASS")

        if not self.url:
            print(f"Error: CONFLUENCE_{self.instance}_URL not set", file=sys.stderr)
            sys.exit(1)

        self.url = self.url.rstrip('/')
        self.cache_file = f"/tmp/confluence_{instance.lower()}_session.json"
        self.cache_ttl = 7 * 24 * 3600

        self.auth_method = self._detect_auth_method()

    def _detect_auth_method(self) -> str:
        if self.basic_user and self.basic_pass:
            return "nginx_browser"
        elif self.pat:
            return "pat"
        elif self.password:
            return "password"
        else:
            print(f"Error: No valid credentials for {self.instance}", file=sys.stderr)
            print("Required: USERNAME + (PAT or PASSWORD)", file=sys.stderr)
            print("Optional: BASIC_USER + BASIC_PASS (for nginx-protected instances)", file=sys.stderr)
            sys.exit(1)

    def get_opener(self) -> urllib.request.OpenerDirector:
        if self.auth_method == "nginx_browser":
            return self._get_session_based_opener()
        else:
            return self._get_simple_opener()

    def _get_simple_opener(self) -> urllib.request.OpenerDirector:
        cookie_jar = CookieJar()
        return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    def _get_session_based_opener(self) -> urllib.request.OpenerDirector:
        session = self._get_or_create_session()

        cookie_jar = CookieJar()

        domain = self.url.replace('https://', '').replace('http://', '')

        cookie_name = session.get('cookie_name', 'seraph.confluence')

        session_cookie = Cookie(
            version=0,
            name=cookie_name,
            value=session['cookie_value'],
            port=None,
            port_specified=False,
            domain=domain,
            domain_specified=True,
            domain_initial_dot=False,
            path='/',
            path_specified=True,
            secure=True,
            expires=None,
            discard=True,
            comment=None,
            comment_url=None,
            rest={},
            rfc2109=False
        )

        cookie_jar.set_cookie(session_cookie)
        return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    def get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if self.auth_method == "nginx_browser":
            nginx_auth = base64.b64encode(f"{self.basic_user}:{self.basic_pass}".encode()).decode()
            headers["Authorization"] = f"Basic {nginx_auth}"

        elif self.auth_method == "pat":
            pat_auth = base64.b64encode(f"{self.username}:{self.pat}".encode()).decode()
            headers["Authorization"] = f"Basic {pat_auth}"

        elif self.auth_method == "password":
            pass_auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers["Authorization"] = f"Basic {pass_auth}"

        return headers

    def _get_or_create_session(self) -> Dict[str, Any]:
        if self._is_cache_valid():
            with open(self.cache_file, 'r') as f:
                session = json.load(f)
                cookie_name = session.get('cookie_name', 'seraph.confluence')
                if self._test_session(session['cookie_value'], cookie_name):
                    return session

        return self._create_session_with_browser()

    def _is_cache_valid(self) -> bool:
        if not os.path.exists(self.cache_file):
            return False

        try:
            with open(self.cache_file, 'r') as f:
                session = json.load(f)

            age = time.time() - session['created_at']
            return age < self.cache_ttl
        except:
            return False

    def _test_session(self, cookie_value: str, cookie_name: str = 'seraph.confluence') -> bool:
        try:
            cookie_jar = CookieJar()
            domain = self.url.replace('https://', '').replace('http://', '')

            session_cookie = Cookie(
                version=0,
                name=cookie_name,
                value=cookie_value,
                port=None,
                port_specified=False,
                domain=domain,
                domain_specified=True,
                domain_initial_dot=False,
                path='/',
                path_specified=True,
                secure=True,
                expires=None,
                discard=True,
                comment=None,
                comment_url=None,
                rest={},
                rfc2109=False
            )

            cookie_jar.set_cookie(session_cookie)
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

            nginx_auth = base64.b64encode(f"{self.basic_user}:{self.basic_pass}".encode()).decode()

            request = urllib.request.Request(f"{self.url}/rest/api/user/current")
            request.add_header("Authorization", f"Basic {nginx_auth}")
            request.add_header("Accept", "application/json")

            with opener.open(request, timeout=5) as response:
                return response.status == 200
        except:
            return False

    def _create_session_with_browser(self) -> Dict[str, Any]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("Error: Playwright not installed", file=sys.stderr)
            print("Install with: pip install playwright && playwright install chromium", file=sys.stderr)
            sys.exit(1)

        print(f"Authenticating to {self.url}...", file=sys.stderr)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                http_credentials={
                    'username': self.basic_user,
                    'password': self.basic_pass
                }
            )

            page = context.new_page()

            try:
                page.goto(f"{self.url}/login.action", wait_until='domcontentloaded', timeout=15000)

                username_filled = False
                for selector in ['#username-field', 'input[name="username"]', '#os_username', 'input[name="os_username"]']:
                    try:
                        page.fill(selector, self.username, timeout=2000)
                        username_filled = True
                        break
                    except:
                        continue

                if not username_filled:
                    print("Error: Could not find username field", file=sys.stderr)
                    browser.close()
                    sys.exit(1)

                password_filled = False
                for selector in ['#password-field', 'input[name="password"]', '#os_password', 'input[name="os_password"]']:
                    try:
                        page.fill(selector, self.password, timeout=2000)
                        password_filled = True
                        break
                    except:
                        continue

                if not password_filled:
                    print("Error: Could not find password field", file=sys.stderr)
                    browser.close()
                    sys.exit(1)

                submit_clicked = False
                for selector in ['button[type="submit"]', 'input[type="submit"]', 'button#login', '#loginButton']:
                    try:
                        page.click(selector, timeout=2000)
                        submit_clicked = True
                        break
                    except:
                        continue

                if not submit_clicked:
                    print("Error: Could not find submit button", file=sys.stderr)
                    browser.close()
                    sys.exit(1)

                page.wait_for_load_state('networkidle', timeout=15000)

                cookies = context.cookies()

                seraph = next((c for c in cookies if c['name'] == 'seraph.confluence'), None)
                jsessionid = next((c for c in cookies if c['name'] == 'JSESSIONID'), None)

                if seraph:
                    cookie_name = 'seraph.confluence'
                    cookie_value = seraph['value']
                elif jsessionid:
                    cookie_name = 'JSESSIONID'
                    cookie_value = jsessionid['value']
                else:
                    print("Error: No session cookie found after login", file=sys.stderr)
                    browser.close()
                    sys.exit(1)

                browser.close()

                session = {
                    'cookie_name': cookie_name,
                    'cookie_value': cookie_value,
                    'created_at': time.time(),
                    'expires_at': time.time() + self.cache_ttl
                }

                with open(self.cache_file, 'w') as f:
                    json.dump(session, f)

                print(f"✓ Authenticated successfully", file=sys.stderr)
                return session

            except Exception as e:
                browser.close()
                print(f"Error: Login failed: {e}", file=sys.stderr)
                sys.exit(1)

    def clear_cache(self):
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            print(f"Cleared session cache for {self.instance}", file=sys.stderr)
