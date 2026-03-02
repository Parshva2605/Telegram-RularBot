#!/usr/bin/env python3
"""
Update doctor statistics - backfill total_cases based on existing reports
"""

import os
from dotenv import load_dotenv
import sys

# Add dashboard to path
sys.path.insert(0, 'dashboard')
from supabase_wrapper import create_client

# Load environment
load_dotenv('.env')

def main():
    print("🔄 UPDATING DOCTOR STATISTICS")
    print("=" * 70)
    
    # Check environment variables
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    # Initialize client
    try:
        supabase = create_client(url, key)
        print("✅ Supabase connected\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False
    
    # Get all doctors
    print("📋 Fetching all doctors...")
    try:
        doctors_response = supabase.table("doctors").select("*").execute()
        doctors = doctors_response.data
        
        if not doctors:
            print("⚠️ No doctors found")
            return False
        
        print(f"✅ Found {len(doctors)} doctor(s)\n")
        
        # Update each doctor's total_cases
        for doctor in doctors:
            phone = doctor.get('phone')
            name = doctor.get('name', 'Unknown')
            current_total = doctor.get('total_cases', 0)
            
            print(f"\n{'='*70}")
            print(f"👨‍⚕️ Dr. {name} ({phone})")
            print(f"{'='*70}")
            print(f"Current total_cases: {current_total}")
            
            # Count reviewed reports for this doctor (get all and count manually)
            reviewed = supabase.table("xray_requests").select("id").eq("doctor_phone", phone).eq("status", "reviewed").execute()
            reviewed_count = len(reviewed.data) if reviewed.data else 0
            
            print(f"Reviewed reports in database: {reviewed_count}")
            
            if reviewed_count != current_total:
                # Update the doctor's total_cases
                try:
                    result = supabase.table("doctors").update({
                        "total_cases": reviewed_count
                    }).eq("phone", phone).execute()
                    
                    print(f"✅ Updated total_cases: {current_total} → {reviewed_count}")
                    print(f"   Update result: {result.data if result else 'No result'}")
                except Exception as e:
                    print(f"❌ Error updating: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"✅ Already up to date")
        
        print(f"\n\n{'='*70}")
        print("✅ ALL DOCTORS UPDATED")
        print(f"{'='*70}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
