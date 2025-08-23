#!/usr/bin/env python3
"""Debug ServiceNow credentials"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

print("ServiceNow Credentials Debug")
print("=" * 30)

# Print loaded values (masking password)
url = os.getenv("SERVICENOW_INSTANCE_URL")
user = os.getenv("SERVICENOW_USER")
pwd = os.getenv("SERVICENOW_PWD")

# Also try personal credentials
personal_user = os.getenv("SERVICENOW_PERSONAL_USER")
personal_pwd = os.getenv("SERVICENOW_PERSONAL_PWD")

print(f"URL: {url}")
print(f"Integration User: {user}")
print(f"Integration Password length: {len(pwd) if pwd else 0}")
print(f"Personal User: {personal_user}")
print(f"Personal Password length: {len(personal_pwd) if personal_pwd else 0}")

# Test basic auth format
if user and pwd:
    import requests
    from requests.auth import HTTPBasicAuth

    # Test with explicit auth
    test_url = f"{url}api/now/table/sys_user?sysparm_limit=1"
    print(f"\nTesting URL: {test_url}")

    # Test integration user
    print("\nTesting Integration User:")
    try:
        response = requests.get(
            test_url, auth=HTTPBasicAuth(user, pwd), headers={"Accept": "application/json"}, timeout=30
        )
        print(f"Status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
        else:
            print("SUCCESS: Integration user authentication worked!")
    except Exception as e:
        print(f"Error: {e}")

    # Test personal user
    if personal_user and personal_pwd:
        print("\nTesting Personal User:")
        try:
            response = requests.get(
                test_url,
                auth=HTTPBasicAuth(personal_user, personal_pwd),
                headers={"Accept": "application/json"},
                timeout=30,
            )
            print(f"Status code: {response.status_code}")
            if response.status_code != 200:
                print(f"Response: {response.text}")
            else:
                print("SUCCESS: Personal user authentication worked!")
        except Exception as e:
            print(f"Error: {e}")
