#!/usr/bin/env python3
"""Test custom Supabase wrapper"""
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client

load_dotenv('.env.doctor')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"Testing custom Supabase wrapper...")
print(f"URL: {url}")
print(f"Key: {key[:30]}...\n")

try:
    client = create_client(url, key)
    print("✅ Client created!")
    
    # Try to query doctors table
    result = client.table('doctors').select("*").limit(1).execute()
    print(f"✅ Query successful!")
    print(f"Count: {result.count}")
    print(f"Data: {result.data}")
    
except Exception as e:
    print(f"❌ Error: {e}")
