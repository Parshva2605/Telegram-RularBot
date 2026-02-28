"""
Download Noto Sans Devanagari font for Hindi support in PDFs
Run this once to enable Hindi text in PDF reports
"""

import os
import urllib.request
import zipfile

def download_hindi_font():
    """Download and extract Noto Sans Devanagari font"""
    
    print("=" * 60)
    print("DOWNLOADING NOTO SANS DEVANAGARI FONT FOR HINDI")
    print("=" * 60)
    print()
    
    # Create fonts directory
    os.makedirs('fonts', exist_ok=True)
    
    # Check if font already exists
    font_path = 'fonts/NotoSansDevanagari-Regular.ttf'
    if os.path.exists(font_path):
        print(f"✅ Font already exists: {font_path}")
        print(f"   File size: {os.path.getsize(font_path)} bytes")
        print()
        print("Hindi support is ready!")
        return True
    
    # Download font directly
    print("📥 Downloading Noto Sans Devanagari font...")
    # Use Google Fonts API
    font_url = 'https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf'
    
    try:
        urllib.request.urlretrieve(font_url, font_path)
        print(f"✅ Downloaded: {font_path}")
        print(f"   Size: {os.path.getsize(font_path)} bytes")
        print()
        
        print("=" * 60)
        print("✅ HINDI FONT INSTALLED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("You can now generate PDFs with Hindi text.")
        print("Run: python report_generator.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading font: {e}")
        print()
        print("MANUAL INSTALLATION:")
        print("1. Download: https://github.com/notofonts/devanagari/raw/main/fonts/NotoSansDevanagari/hinted/ttf/NotoSansDevanagari-Regular.ttf")
        print("2. Save as: fonts/NotoSansDevanagari-Regular.ttf")
        print()
        return False

if __name__ == "__main__":
    success = download_hindi_font()
    
    if success:
        print("🎉 Ready to generate bilingual PDFs!")
    else:
        print("⚠️  Please install font manually")
