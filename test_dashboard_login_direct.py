"""
Direct test of dashboard login logic
Simulates exactly what the dashboard does
"""

import os
from dotenv import load_dotenv
import sys

# Add dashboard to path to import supabase_wrapper
sys.path.insert(0, 'dashboard')

from supabase_wrapper import create_client

# Load dashboard environment
load_dotenv('dashboard/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("=" * 60)
print("🔐 TESTING DASHBOARD LOGIN (Exact simulation)")
print("=" * 60)
print()

print(f"Supabase URL: {SUPABASE_URL}")
print(f"Supabase Key: {SUPABASE_KEY[:30]}...")
print()

# Test credentials
test_credentials = [
    ("+919876543210", "TEST1234", "Dr. Shah"),
    ("+919999999999", "TEST1234", "Dr. Test Kumar"),
]

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created")
    print()
    
    for phone, code, expected_name in test_credentials:
        print("-" * 60)
        print(f"Testing: {expected_name}")
        print(f"Phone: {phone}")
        print(f"Code: {code}")
        print()
        
        try:
            # This is EXACTLY what the dashboard does
            response = supabase.table("doctors").select("*").eq("phone", phone).eq("access_code", code).execute()
            
            print(f"Response data: {response.data}")
            print(f"Response count: {response.count if hasattr(response, 'count') else 'N/A'}")
            print()
            
            if response.data and len(response.data) > 0:
                doctor = response.data[0]
                print("✅ LOGIN SUCCESSFUL!")
                print(f"   Name: {doctor.get('name', 'Unknown')}")
                print(f"   Phone: {doctor.get('phone')}")
                print(f"   PHC: {doctor.get('phc', 'N/A')}")
                print(f"   MCI: {doctor.get('mci_reg', 'N/A')}")
                print(f"   Rating: {doctor.get('rating', 0)}")
                print(f"   Total Cases: {doctor.get('total_cases', 0)}")
                print(f"   Active: {doctor.get('active', False)}")
                print()
            else:
                print("❌ LOGIN FAILED!")
                print("   No matching doctor found")
                print()
                
                # Debug: Check if phone exists
                phone_check = supabase.table("doctors").select("*").eq("phone", phone).execute()
                if phone_check.data:
                    print(f"   ℹ️  Phone {phone} EXISTS in database")
                    print(f"   But access code doesn't match!")
                    print(f"   Expected: {code}")
                    print(f"   In DB: {phone_check.data[0].get('access_code')}")
                else:
                    print(f"   ℹ️  Phone {phone} NOT FOUND in database")
                print()
        
        except Exception as e:
            print(f"❌ ERROR during login test: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    # Show all doctors for reference
    print("=" * 60)
    print("📋 ALL DOCTORS IN DATABASE")
    print("=" * 60)
    print()
    
    all_doctors = supabase.table("doctors").select("*").execute()
    
    if all_doctors.data:
        for i, doc in enumerate(all_doctors.data, 1):
            print(f"{i}. {doc.get('name', 'Unknown')}")
            print(f"   Phone: {doc.get('phone')}")
            print(f"   Access Code: {doc.get('access_code')}")
            print(f"   Active: {doc.get('active', False)}")
            print()
    else:
        print("⚠️  No doctors found!")
        print()

except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
print("✅ TEST COMPLETE")
print("=" * 60)
