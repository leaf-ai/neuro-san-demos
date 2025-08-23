#!/usr/bin/env python3
"""Test basic ServiceNow instance accessibility"""

import sys

import requests

instance_url = "https://appoxiotechnologiesincdemo3.service-now.com/"

print(f"Testing ServiceNow instance: {instance_url}")
print("=" * 50)

# Test 1: Basic instance accessibility
print("1. Testing basic instance accessibility...")
try:
    response = requests.get(instance_url, timeout=10)
    print(f"   Status: {response.status_code}")
    print("   Instance is accessible")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# Test 2: Test login page
print("\n2. Testing login page...")
try:
    login_url = f"{instance_url}login.do"
    response = requests.get(login_url, timeout=10)
    print(f"   Login page status: {response.status_code}")
    if "ServiceNow" in response.text:
        print("   Confirmed ServiceNow instance")
    else:
        print("   Warning: May not be a ServiceNow instance")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Test API endpoint accessibility (without auth)
print("\n3. Testing API endpoint accessibility...")
try:
    api_url = f"{instance_url}api/now/table/sys_user?sysparm_limit=1"
    response = requests.get(api_url, timeout=10)
    print(f"   API endpoint status: {response.status_code}")
    if response.status_code == 401:
        print("   Good: API requires authentication (expected)")
    elif response.status_code == 200:
        print("   Warning: API accessible without auth (unexpected)")
    else:
        print(f"   API response: {response.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\nInstance accessibility test completed.")
print("If authentication is still failing, the credentials may be incorrect")
print("or the instance may require different auth methods (OAuth, MFA, etc.)")
