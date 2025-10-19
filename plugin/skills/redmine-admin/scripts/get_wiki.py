#!/usr/bin/env python3

import sys
import json
import argparse
import re
from urllib.parse import urlparse
from redmine_api import RedmineAPI


def parse_wiki_url(url):
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')

    if 'wiki' not in path_parts:
        return None, None

    wiki_index = path_parts.index('wiki')

    if 'projects' in path_parts and wiki_index > 0:
        project_index = path_parts.index('projects')
        if project_index + 1 < len(path_parts):
            project_id = path_parts[project_index + 1]
            if wiki_index + 1 < len(path_parts):
                page_name = path_parts[wiki_index + 1]
                return project_id, page_name

    return None, None


def main():
    parser = argparse.ArgumentParser(description="Get Redmine wiki page")
    parser.add_argument("--url", help="Full Redmine wiki URL")
    parser.add_argument("--project-id", help="Project identifier")
    parser.add_argument("--page", help="Wiki page name")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format (default: text)")

    args = parser.parse_args()

    if args.url:
        project_id, page_name = parse_wiki_url(args.url)
        if not project_id or not page_name:
            print(f"Error: Could not parse wiki URL: {args.url}", file=sys.stderr)
            print("Expected format: https://redmine.example.com/projects/PROJECT/wiki/PAGE", file=sys.stderr)
            sys.exit(1)
    elif args.project_id and args.page:
        project_id = args.project_id
        page_name = args.page
    else:
        print("Error: Either --url or both --project-id and --page must be provided", file=sys.stderr)
        sys.exit(1)

    api = RedmineAPI()

    try:
        endpoint = f"projects/{project_id}/wiki/{page_name}.json"
        result = api.get(endpoint)

        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            wiki_page = result.get("wiki_page", {})
            title = wiki_page.get("title", "")
            text = wiki_page.get("text", "")
            version = wiki_page.get("version", "")
            author = wiki_page.get("author", {}).get("name", "Unknown")
            updated_on = wiki_page.get("updated_on", "")

            print(f"Title: {title}")
            print(f"Project: {project_id}")
            print(f"Page: {page_name}")
            print(f"Version: {version}")
            print(f"Author: {author}")
            print(f"Updated: {updated_on}")
            print("-" * 80)
            print(text)
    except SystemExit:
        raise


if __name__ == "__main__":
    main()
