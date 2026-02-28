"""
Test script to verify doctor login credentials
Run this to check if the test doctor exists in database
"""

import os
from dotenv import load_dotenv
from supabase_wrapper import create_client

load_dotenv('dashboard/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("=== TESTING DOCTOR LOGIN ===")
print(f"Supabase URL: {SUPABASE_URL}")
print(f"Supabase Key: {SUPABASE_KEY[:30]}...")
print()

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase")
    print()
    
    # Test 1: Check if doctors table exists
    print("Test 1: Checking doctors table...")
    all_doctors = supabase.table("doctors").select("*").execute()
    print(f"✅ Found {len(all_doctors.data) if all_doctors.data else 0} doctors in database")
    print()
    
    # Test 2: List all doctors
    if all_doctors.data:
        print("All doctors in database:")
        for doc in all_doctors.data:
            print(f"  - Phone: {doc.get('phone')}, Code: {doc.get('access_code')}, Name: {doc.get('name')}")
        print()
    
    # Test 3: Try to find test doctor
    print("Test 3: Looking for test doctor (+919999999999)...")
    test_doctor = supabase.table("doctors").select("*").eq("phone", "+919999999999").execute()
    
    if test_doctor.data and len(test_doctor.data) > 0:
        print("✅ Test doctor found!")
        doc = test_doctor.data[0]
        print(f"  Name: {doc.get('name')}")
        print(f"  Phone: {doc.get('phone')}")
        print(f"  Access Code: {doc.get('access_code')}")
        print(f"  MCI: {doc.get('mci_reg')}")
        print(f"  PHC: {doc.get('phc')}")
        print(f"  Active: {doc.get('active')}")
    else:
        print("❌ Test doctor NOT found!")
        print("   Run this SQL in Supabase:")
        print("""
        INSERT INTO doctors (phone, telegram_id, access_code, name, mci_reg, phc, rating, total_cases, active)
        VALUES ('+919999999999', 999999999, 'TEST1234', 'Dr. Test Kumar', 'TEST12345', 'Test PHC', 5.0, 0, true);
        """)
    print()
    
    # Test 4: Try login with test credentials
    print("Test 4: Testing login with credentials...")
    phone = "+919999999999"
    code = "TEST1234"
    
    login_result = supabase.table("doctors").select("*").eq("phone", phone).eq("access_code", code).execute()
    
    if login_result.data and len(login_result.data) > 0:
        print("✅ LOGIN SUCCESSFUL!")
        print(f"   Welcome Dr. {login_result.data[0].get('name')}")
        print()
        print("Use these credentials in dashboard:")
        print(f"   Phone: {phone}")
        print(f"   Access Code: {code}")
    else:
        print("❌ LOGIN FAILED!")
        print("   Credentials don't match")
        print()
        print("Checking what went wrong...")
        
        # Check phone only
        phone_check = supabase.table("doctors").select("*").eq("phone", phone).execute()
        if phone_check.data:
            print(f"   ✅ Phone found: {phone}")
            print(f"   ❌ But access code doesn't match!")
            print(f"   Expected: {code}")
            print(f"   In database: {phone_check.data[0].get('access_code')}")
        else:
            print(f"   ❌ Phone not found: {phone}")
            print("   Doctor doesn't exist in database")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=== TEST COMPLETE ===")
