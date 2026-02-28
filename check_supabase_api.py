#!/usr/bin/env python3
"""Check Supabase API directly"""
import requests
import os
from dotenv import load_dotenv

load_dotenv('.env.doctor')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"Testing direct API call...")
print(f"URL: {url}")
print(f"Key: {key}\n")

# Try REST API call
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}'
}

try:
    response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("\n✅ API key is VALID!")
    else:
        print(f"\n❌ API key rejected: {response.status_code}")
        
except Exception as e:
    print(f"❌ Connection error: {e}")
