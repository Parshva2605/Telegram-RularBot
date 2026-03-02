#!/usr/bin/env python3
"""
Check what's in the xray_requests table for report_pdf_url
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
    print("🔍 CHECKING XRAY_REQUESTS TABLE FOR REPORTS")
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
        print("✅ Supabase connected")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False
    
    # Fetch all xray_requests
    print("\n📋 FETCHING ALL X-RAY REQUESTS")
    print("-" * 70)
    try:
        response = supabase.table("xray_requests").select("*").order("created_at", desc=True).execute()
        requests = response.data
        
        if requests:
            print(f"✅ Found {len(requests)} request(s)\n")
            
            for idx, req in enumerate(requests, 1):
                print(f"\n{'='*70}")
                print(f"REQUEST #{idx} - ID: {req.get('id')}")
                print(f"{'='*70}")
                print(f"Patient: {req.get('patient_name')} ({req.get('age')}y)")
                print(f"Status: {req.get('status')}")
                print(f"Created: {req.get('created_at')}")
                print(f"Reviewed: {req.get('reviewed_at')}")
                print(f"Doctor Phone: {req.get('doctor_phone')}")
                
                # Check report_pdf_url
                pdf_url = req.get('report_pdf_url')
                if pdf_url:
                    print(f"\n📄 REPORT PDF URL: {pdf_url}")
                    
                    # Check if file exists
                    if os.path.exists(pdf_url):
                        file_size = os.path.getsize(pdf_url) / 1024  # KB
                        print(f"   ✅ File EXISTS - Size: {file_size:.1f} KB")
                    else:
                        print(f"   ❌ File NOT FOUND at: {pdf_url}")
                        
                        # Check if it exists with absolute path
                        abs_path = os.path.abspath(pdf_url)
                        if os.path.exists(abs_path):
                            print(f"   ✅ Found at absolute path: {abs_path}")
                        else:
                            print(f"   ❌ Not found at absolute path either")
                else:
                    print(f"\n⚠️ NO REPORT PDF URL (report_pdf_url is NULL)")
                
                # Check if has AI report
                if req.get('ai_report'):
                    print(f"\n🤖 AI Report: {req.get('ai_report')[:100]}...")
                
                # Check if has doctor notes
                if req.get('doctor_notes'):
                    print(f"\n📝 Doctor Notes: {req.get('doctor_notes')[:100]}...")
        else:
            print("⚠️ No requests found in database")
    except Exception as e:
        print(f"❌ Failed to fetch requests: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check reports folder
    print(f"\n\n{'='*70}")
    print("📁 CHECKING REPORTS FOLDER")
    print(f"{'='*70}")
    
    reports_dir = "reports"
    if os.path.exists(reports_dir):
        files = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]
        print(f"✅ Found {len(files)} PDF file(s) in {reports_dir}/\n")
        
        for pdf_file in sorted(files):
            full_path = os.path.join(reports_dir, pdf_file)
            file_size = os.path.getsize(full_path) / 1024  # KB
            print(f"   📄 {pdf_file} - {file_size:.1f} KB")
    else:
        print(f"❌ Reports folder not found: {reports_dir}")
    
    print(f"\n{'='*70}")
    print("✅ CHECK COMPLETE")
    print(f"{'='*70}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
