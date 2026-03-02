#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, 'dashboard')
from supabase_wrapper import create_client

load_dotenv('.env')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Get all reviewed requests
reviewed = supabase.table("xray_requests").select("id, patient_name, doctor_phone, status").eq("status", "reviewed").execute()

print(f"Total reviewed requests: {len(reviewed.data) if reviewed.data else 0}")
print()

if reviewed.data:
    for r in reviewed.data:
        print(f"ID: {r['id']}, Patient: {r['patient_name']}, Doctor: {r.get('doctor_phone', 'N/A')}, Status: {r['status']}")
