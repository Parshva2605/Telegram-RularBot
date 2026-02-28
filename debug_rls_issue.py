"""
Debug RLS policy issue
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv('dashboard/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("Testing RLS Policies")
print("=" * 60)
print()

# Test 1: Get all doctors (no filter)
print("Test 1: Get ALL doctors (no filter)")
url1 = f"{SUPABASE_URL}/rest/v1/doctors"
response1 = requests.get(url1, headers=headers)
print(f"Status: {response1.status_code}")
print(f"Count: {len(response1.json()) if response1.status_code == 200 else 0}")
print(f"Response: {response1.text[:200]}...")
print()

# Test 2: Filter by phone only
print("Test 2: Filter by phone only")
url2 = f"{SUPABASE_URL}/rest/v1/doctors?phone=eq.+919876543210"
response2 = requests.get(url2, headers=headers)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text}")
print()

# Test 3: Filter by phone AND access_code
print("Test 3: Filter by phone AND access_code")
url3 = f"{SUPABASE_URL}/rest/v1/doctors?phone=eq.+919876543210&access_code=eq.TEST1234"
response3 = requests.get(url3, headers=headers)
print(f"Status: {response3.status_code}")
print(f"Response: {response3.text}")
print()

# Test 4: Try with select parameter
print("Test 4: With select parameter")
url4 = f"{SUPABASE_URL}/rest/v1/doctors?select=*&phone=eq.+919876543210&access_code=eq.TEST1234"
response4 = requests.get(url4, headers=headers)
print(f"Status: {response4.status_code}")
print(f"Response: {response4.text}")
print()

# Test 5: Check if it's URL encoding issue
print("Test 5: Without + in phone number")
url5 = f"{SUPABASE_URL}/rest/v1/doctors?phone=eq.919876543210&access_code=eq.TEST1234"
response5 = requests.get(url5, headers=headers)
print(f"Status: {response5.status_code}")
print(f"Response: {response5.text}")
print()

# Test 6: Check actual phone format in database
print("Test 6: Get all doctors to see actual phone format")
all_docs = response1.json() if response1.status_code == 200 else []
if all_docs:
    print("Phone numbers in database:")
    for doc in all_docs:
        print(f"  - '{doc.get('phone')}' (repr: {repr(doc.get('phone'))})")
        print(f"    Access code: '{doc.get('access_code')}'")
