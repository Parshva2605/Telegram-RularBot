"""
Test with role header to bypass RLS
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv('dashboard/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("Testing with different header combinations...")
print()

# Test 1: Standard headers
print("Test 1: Standard headers")
headers1 = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}
url = f"{SUPABASE_URL}/rest/v1/doctors?phone=eq.+919876543210&access_code=eq.TEST1234"
response1 = requests.get(url, headers=headers1)
print(f"Status: {response1.status_code}")
print(f"Response: {response1.text}")
print()

# Test 2: With Prefer header to bypass RLS
print("Test 2: With Prefer header")
headers2 = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
response2 = requests.get(url, headers=headers2)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text}")
print()

# Test 3: Try without Authorization header
print("Test 3: Only apikey header")
headers3 = {
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json"
}
response3 = requests.get(url, headers=headers3)
print(f"Status: {response3.status_code}")
print(f"Response: {response3.text}")
print()

# Test 4: Get all and filter in Python
print("Test 4: Get all and filter in Python (workaround)")
url_all = f"{SUPABASE_URL}/rest/v1/doctors"
response_all = requests.get(url_all, headers=headers1)
if response_all.status_code == 200:
    all_doctors = response_all.json()
    filtered = [d for d in all_doctors if d.get('phone') == '+919876543210' and d.get('access_code') == 'TEST1234']
    print(f"Found {len(filtered)} matching doctor(s)")
    if filtered:
        print(f"✅ LOGIN WOULD WORK with client-side filtering!")
        print(f"Doctor: {filtered[0].get('name')}")
