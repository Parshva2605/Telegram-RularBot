#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, 'dashboard')
from supabase_wrapper import create_client

load_dotenv('.env')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=== CHECKING APPOINTMENTS ===\n")

# Get all appointments
response = supabase.table('appointments').select('*').execute()

if response.data:
    print(f"Total appointments: {len(response.data)}\n")
    
    for apt in response.data:
        print(f"ID: {apt['id']}")
        print(f"Patient Telegram ID: {apt['patient_telegram_id']}")
        print(f"Patient Name: {apt['patient_name']}")
        print(f"Doctor: {apt['doctor_name']}")
        print(f"Date: {apt['appointment_date']}")
        print(f"Status: {apt['status']}")
        print(f"Reason: {apt['reason']}")
        print("-" * 50)
else:
    print("No appointments found in database")
