#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import requests

load_dotenv('.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

# Direct API call to update Dr. A
phone = "+919638622240"
update_url = f"{url}/rest/v1/doctors?phone=eq.{phone}"

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

data = {"total_cases": 8}

print(f"Updating doctor with phone: {phone}")
print(f"URL: {update_url}")
print(f"Data: {data}")

response = requests.patch(update_url, json=data, headers=headers)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("\n✅ Update successful!")
    result = response.json()
    if result:
        print(f"Updated: {result}")
    else:
        print("⚠️ No rows returned (might be RLS policy issue)")
else:
    print(f"\n❌ Update failed: {response.text}")
