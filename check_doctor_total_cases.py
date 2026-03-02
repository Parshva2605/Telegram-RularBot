#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, 'dashboard')
from supabase_wrapper import create_client

load_dotenv('.env')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Get Dr. A's data
doctor = supabase.table("doctors").select("*").eq("phone", "+919638622240").execute()

if doctor.data:
    d = doctor.data[0]
    print(f"Dr. {d['name']}")
    print(f"Phone: {d['phone']}")
    print(f"Total Cases in DB: {d.get('total_cases', 'NOT SET')}")
    print(f"Rating in DB: {d.get('rating', 'NOT SET')}")
else:
    print("Doctor not found")
