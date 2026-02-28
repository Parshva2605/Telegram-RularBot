#!/usr/bin/env python3
"""Test Supabase key formats"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('.env.doctor')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"Testing Supabase connection...")
print(f"URL: {url}")
print(f"Key format: {key[:20]}... (length: {len(key)})")
print(f"Key starts with: {key[:3]}")

try:
    client = create_client(url, key)
    print("✅ Client created successfully!")
    
    # Try to query
    result = client.table('doctors').select('*', count='exact').limit(1).execute()
    print(f"✅ Query successful! Count: {result.count}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nThe key format is invalid.")
    print("Please get the correct anon key from Supabase dashboard.")
    print("It should be a long JWT token starting with 'eyJ'")
