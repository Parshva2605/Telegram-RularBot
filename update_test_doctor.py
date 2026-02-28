"""Quick script to update test doctor access code"""
from dotenv import load_dotenv
import os
from supabase_wrapper import create_client

load_dotenv('dashboard/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("Updating Dr. Test Kumar access code...")
result = supabase.table('doctors').update({'access_code': 'TEST1234'}).eq('phone', '+919999999999').execute()
print(f"✅ Update complete")

# Verify
check = supabase.table('doctors').select('*').eq('phone', '+919999999999').execute()
if check.data:
    print(f"Verified: Access code is now {check.data[0]['access_code']}")
