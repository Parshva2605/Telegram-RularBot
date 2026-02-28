"""
Debug the actual HTTP request being made
"""

import os
from dotenv import load_dotenv
import sys
import requests

sys.path.insert(0, 'dashboard')
from supabase_wrapper import create_client

load_dotenv('dashboard/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("Testing direct HTTP request...")
print()

# Test 1: Direct HTTP request (what should work)
url = f"{SUPABASE_URL}/rest/v1/doctors?phone=eq.+919876543210&access_code=eq.TEST1234"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print(f"URL: {url}")
print()

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Test 2: Using wrapper
print("=" * 60)
print("Testing with wrapper...")
print()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Add debug to see what URL is being built
table = supabase.table("doctors")
query = table.select("*").eq("phone", "+919876543210").eq("access_code", "TEST1234")

print(f"Base URL: {query.url}")
print(f"Filters: {query.filters}")
print()

result = query.execute()
print(f"Result data: {result.data}")
print(f"Result count: {result.count}")
