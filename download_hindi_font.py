"""
Download Mangal font for Hindi support in PDFs
Mangal is a standard Windows Hindi font that works well with fpdf2
"""

import os
import urllib.request

def download_hindi_font():
    """Download Mangal font for Hindi support"""
    
    print("=" * 60)
    print("SETTING UP HINDI FONT FOR PDF")
    print("=" * 60)
    print()
    
    # Create fonts directory
    os.makedirs('fonts', exist_ok=True)
    
    # Check if font already exists
    font_path = 'fonts/mangal.ttf'
    
    # Check Windows fonts folder first
    windows_mangal = 'C:/Windows/Fonts/mangal.ttf'
    if os.path.exists(windows_mangal):
        print(f"✅ Found Mangal font in Windows: {windows_mangal}")
        print("   Copying to fonts/ folder...")
        import shutil
        shutil.copy(windows_mangal, font_path)
        print(f"✅ Copied to: {font_path}")
        print(f"   File size: {os.path.getsize(font_path)} bytes")
        print()
        print("=" * 60)
        print("✅ HINDI FONT READY!")
        print("=" * 60)
        print()
        return True
    
    if os.path.exists(font_path):
        print(f"✅ Font already exists: {font_path}")
        print(f"   File size: {os.path.getsize(font_path)} bytes")
        print()
        print("Hindi support is ready!")
        return True
    
    # Try to download Noto Sans Devanagari (static version)
    print("📥 Downloading Noto Sans Devanagari...")
    # Use a working direct link
    font_url = 'https://noto-website-2.storage.googleapis.com/pkgs/NotoSansDevanagari-unhinted.zip'
    zip_path = 'fonts/noto.zip'
    
    try:
        import zipfile
        urllib.request.urlretrieve(font_url, zip_path)
        print(f"✅ Downloaded: {zip_path}")
        
        # Extract Regular font
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if 'Regular.ttf' in file and 'NotoSansDevanagari' in file:
                    zip_ref.extract(file, 'fonts/')
                    extracted = os.path.join('fonts', file)
                    os.rename(extracted, font_path)
                    print(f"✅ Extracted: {font_path}")
                    break
        
        # Clean up
        os.remove(zip_path)
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
        print(f"❌ Error: {e}")
        print()
        print("MANUAL INSTALLATION:")
        print("1. Download any Hindi TTF font (Noto Sans Devanagari, Mangal, etc.)")
        print("2. Save as: fonts/mangal.ttf")
        print()
        return False

if __name__ == "__main__":
    success = download_hindi_font()
    
    if success:
        print("🎉 Ready to generate bilingual PDFs!")
    else:
        print("⚠️  Font setup incomplete")
