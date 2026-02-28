"""
Quick script to verify existing doctors and optionally create test doctor
Run this before testing the dashboard
"""

import os
from dotenv import load_dotenv
from supabase_wrapper import create_client

# Load environment
load_dotenv('dashboard/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("=" * 60)
print("🔐 DOCTOR DASHBOARD - LOGIN VERIFICATION")
print("=" * 60)
print()

try:
    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase")
    print(f"   URL: {SUPABASE_URL}")
    print()
    
    # Get all doctors
    print("📋 Checking existing doctors...")
    all_doctors = supabase.table("doctors").select("*").execute()
    
    if all_doctors.data:
        print(f"✅ Found {len(all_doctors.data)} doctor(s) in database:")
        print()
        
        for i, doc in enumerate(all_doctors.data, 1):
            print(f"   {i}. {doc.get('name', 'Unknown')}")
            print(f"      Phone: {doc.get('phone')}")
            print(f"      Access Code: {doc.get('access_code')}")
            print(f"      PHC: {doc.get('phc', 'N/A')}")
            print(f"      MCI: {doc.get('mci_reg', 'N/A')}")
            print(f"      Active: {doc.get('active', False)}")
            print()
    else:
        print("⚠️  No doctors found in database")
        print()
    
    # Check for recommended test doctor
    print("=" * 60)
    print("🎯 RECOMMENDED LOGIN CREDENTIALS")
    print("=" * 60)
    print()
    
    # Option 1: Check for +919876543210
    test1 = [d for d in all_doctors.data if d.get('phone') == '+919876543210'] if all_doctors.data else []
    
    if test1:
        doc = test1[0]
        print("✅ OPTION 1: Dr. Shah (Already exists!)")
        print(f"   Phone: +919876543210")
        print(f"   Access Code: {doc.get('access_code')}")
        print(f"   Name: {doc.get('name')}")
        print()
        print("   👉 USE THIS TO LOGIN NOW!")
        print()
    
    # Option 2: Check for +919999999999
    test2 = [d for d in all_doctors.data if d.get('phone') == '+919999999999'] if all_doctors.data else []
    
    if test2:
        doc = test2[0]
        print("✅ OPTION 2: Dr. Test Kumar (Already exists!)")
        print(f"   Phone: +919999999999")
        print(f"   Access Code: {doc.get('access_code')}")
        print(f"   Name: {doc.get('name')}")
        print()
    else:
        print("⚠️  OPTION 2: Dr. Test Kumar (Not found)")
        print("   Phone: +919999999999")
        print()
        
        # Ask if user wants to create
        create = input("   Do you want to create this test doctor? (y/n): ").strip().lower()
        
        if create == 'y':
            print()
            print("   Creating test doctor...")
            
            try:
                result = supabase.table("doctors").insert({
                    "phone": "+919999999999",
                    "telegram_id": 999999999,
                    "access_code": "TEST1234",
                    "name": "Dr. Test Kumar",
                    "mci_reg": "TEST12345",
                    "phc": "Test PHC",
                    "rating": 5.0,
                    "total_cases": 0,
                    "active": True
                }).execute()
                
                print("   ✅ Test doctor created successfully!")
                print()
                print("   Login with:")
                print("   Phone: +919999999999")
                print("   Access Code: TEST1234")
                print()
            except Exception as e:
                # Try update instead
                print("   Doctor might exist, trying update...")
                try:
                    result = supabase.table("doctors").update({
                        "access_code": "TEST1234",
                        "name": "Dr. Test Kumar",
                        "mci_reg": "TEST12345",
                        "phc": "Test PHC",
                        "active": True
                    }).eq("phone", "+919999999999").execute()
                    
                    print("   ✅ Test doctor updated successfully!")
                    print()
                    print("   Login with:")
                    print("   Phone: +919999999999")
                    print("   Access Code: TEST1234")
                    print()
                except Exception as e2:
                    print(f"   ❌ Error: {e2}")
                    print()
        else:
            print("   Skipped creating test doctor")
            print()
    
    # Final instructions
    print("=" * 60)
    print("🚀 NEXT STEPS")
    print("=" * 60)
    print()
    print("1. Start the dashboard:")
    print("   cd dashboard")
    print("   streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py")
    print()
    print("2. Login with one of the credentials above")
    print()
    print("3. Verify all tabs work:")
    print("   - Live Queue")
    print("   - My Reports")
    print("   - Statistics")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
print("✅ VERIFICATION COMPLETE")
print("=" * 60)
