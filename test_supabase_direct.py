#!/usr/bin/env python3
"""Test Supabase with direct client creation"""
from supabase._sync.client import SyncClient, ClientOptions
import os
from dotenv import load_dotenv

load_dotenv('.env.doctor')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"Testing Supabase with custom options...")
print(f"URL: {url}")
print(f"Key: {key[:30]}...\n")

try:
    # Try with schema validation disabled
    options = ClientOptions(
        schema="public",
        headers={},
        auto_refresh_token=False,
        persist_session=False
    )
    
    client = SyncClient(url, key, options)
    print("✅ Client created!")
    
    # Try to query
    result = client.table('doctors').select('*', count='exact').limit(1).execute()
    print(f"✅ Query successful! Count: {result.count}")
    print(f"Data: {result.data}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
