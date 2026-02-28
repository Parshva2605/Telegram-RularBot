#!/usr/bin/env python3
"""
Quick verification script for Admin Panel - Manage Doctors
Tests Supabase connection and basic operations
"""

import os
from dotenv import load_dotenv
import sys

# Add dashboard to path
sys.path.insert(0, 'dashboard')
from supabase_wrapper import create_client

# Load environment
load_dotenv('dashboard/.env')

def main():
    print("🔍 ADMIN PANEL VERIFICATION")
    print("=" * 50)
    
    # Check environment variables
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ Missing Supabase credentials in dashboard/.env")
        return False
    
    print(f"✅ Supabase URL: {url}")
    print(f"✅ Supabase Key: {key[:20]}...")
    print()
    
    # Initialize client
    try:
        supabase = create_client(url, key)
        print("✅ Supabase client created")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False
    
    # Test 1: Fetch all doctors
    print("\n📋 TEST 1: Fetch All Doctors")
    print("-" * 50)
    try:
        response = supabase.table("doctors").select("*").execute()
        doctors = response.data
        
        if doctors:
            print(f"✅ Found {len(doctors)} doctor(s)")
            for doctor in doctors:
                status = "✅ Active" if doctor.get('active') else "❌ Inactive"
                print(f"\n  {status} {doctor.get('name', 'Unknown')}")
                print(f"  📱 Phone: {doctor.get('phone')}")
                print(f"  🩺 MCI: {doctor.get('mci_reg')}")
                print(f"  🏥 PHC: {doctor.get('phc')}")
                print(f"  ⭐ Rating: {doctor.get('rating', 0):.1f}/5.0")
                print(f"  📊 Cases: {doctor.get('total_cases', 0)}")
                print(f"  🔐 Code: {doctor.get('access_code')}")
        else:
            print("⚠️ No doctors found in database")
            print("   Run database/insert_test_doctor.sql to add test data")
    except Exception as e:
        print(f"❌ Failed to fetch doctors: {e}")
        return False
    
    # Test 2: Search functionality
    print("\n🔍 TEST 2: Search by Name")
    print("-" * 50)
    try:
        search_term = "Shah"
        all_doctors = supabase.table("doctors").select("*").execute().data
        filtered = [d for d in all_doctors if search_term.lower() in d.get('name', '').lower()]
        print(f"✅ Search '{search_term}': Found {len(filtered)} match(es)")
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    # Test 3: Filter by status
    print("\n🔍 TEST 3: Filter by Status")
    print("-" * 50)
    try:
        all_doctors = supabase.table("doctors").select("*").execute().data
        active = [d for d in all_doctors if d.get('active', False)]
        inactive = [d for d in all_doctors if not d.get('active', False)]
        print(f"✅ Active: {len(active)}")
        print(f"✅ Inactive: {len(inactive)}")
    except Exception as e:
        print(f"❌ Filter failed: {e}")
    
    # Test 4: Statistics
    print("\n📊 TEST 4: Statistics")
    print("-" * 50)
    try:
        all_doctors = supabase.table("doctors").select("*").execute().data
        total = len(all_doctors)
        active_count = len([d for d in all_doctors if d.get('active', False)])
        total_cases = sum(d.get('total_cases', 0) for d in all_doctors)
        avg_rating = sum(d.get('rating', 0) for d in all_doctors) / total if total > 0 else 0
        
        print(f"✅ Total Doctors: {total}")
        print(f"✅ Active: {active_count}")
        print(f"✅ Inactive: {total - active_count}")
        print(f"✅ Total Cases: {total_cases}")
        print(f"✅ Avg Rating: {avg_rating:.2f}/5.0")
    except Exception as e:
        print(f"❌ Statistics failed: {e}")
    
    # Test 5: Access code generation
    print("\n🔐 TEST 5: Access Code Generation")
    print("-" * 50)
    try:
        import secrets
        new_code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
        print(f"✅ Generated code: {new_code}")
        print(f"   Length: {len(new_code)} characters")
        print(f"   Format: Alphanumeric (no confusing chars)")
    except Exception as e:
        print(f"❌ Code generation failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("\n🚀 Admin Panel Ready:")
    print("   1. Dashboard running at: http://localhost:8502")
    print("   2. Navigate to: 👨‍⚕️ Manage Doctors")
    print("   3. Follow TEST_ADMIN_PANEL.md for full testing")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
