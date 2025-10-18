#!/usr/bin/env python3

import sys
import json
from redmine_api import RedmineAPI


def main():
    api = RedmineAPI()
    result = api.get("users/current.json")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
