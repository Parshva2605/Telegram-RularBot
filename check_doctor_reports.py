#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, 'dashboard')
from supabase_wrapper import create_client

load_dotenv('.env')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Get all requests grouped by status
print("=== ALL REQUESTS BY STATUS ===\n")

for status in ['pending', 'reviewed', 'sent']:
    requests = supabase.table("xray_requests").select("id, patient_name, doctor_phone, status").eq("status", status).execute()
    
    print(f"\n{status.upper()}: {len(requests.data) if requests.data else 0} requests")
    
    if requests.data:
        # Group by doctor
        by_doctor = {}
        for r in requests.data:
            doc = r.get('doctor_phone', 'N/A')
            if doc not in by_doctor:
                by_doctor[doc] = []
            by_doctor[doc].append(r)
        
        for doc, reqs in by_doctor.items():
            print(f"  {doc}: {len(reqs)} cases")
            for r in reqs[:3]:  # Show first 3
                print(f"    - ID {r['id']}: {r['patient_name']}")

