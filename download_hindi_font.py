"""
Download DejaVu Sans font for Hindi support in PDFs
Run this once to enable Hindi text in PDF reports
"""

import os
import urllib.request
import zipfile

def download_dejavu_font():
    """Download and extract DejaVu Sans font"""
    
    print("=" * 60)
    print("DOWNLOADING DEJAVU SANS FONT FOR HINDI SUPPORT")
    print("=" * 60)
    print()
    
    # Create fonts directory
    os.makedirs('fonts', exist_ok=True)
    
    # Check if font already exists
    font_path = 'fonts/DejaVuSans.ttf'
    if os.path.exists(font_path):
        print(f"✅ Font already exists: {font_path}")
        print(f"   File size: {os.path.getsize(font_path)} bytes")
        print()
        print("Hindi support is ready!")
        return True
    
    # Download font package
    print("📥 Downloading DejaVu Fonts package...")
    font_url = 'https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip'
    zip_path = 'fonts/dejavu-fonts.zip'
    
    try:
        urllib.request.urlretrieve(font_url, zip_path)
        print(f"✅ Downloaded: {zip_path}")
        print(f"   Size: {os.path.getsize(zip_path)} bytes")
        print()
        
        # Extract the specific font we need
        print("📦 Extracting DejaVuSans.ttf...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find DejaVuSans.ttf in the zip
            for file in zip_ref.namelist():
                if file.endswith('DejaVuSans.ttf'):
                    # Extract to fonts/ folder
                    zip_ref.extract(file, 'fonts/')
                    
                    # Move to root of fonts/ folder
                    extracted_path = os.path.join('fonts', file)
                    os.rename(extracted_path, font_path)
                    
                    print(f"✅ Extracted: {font_path}")
                    print(f"   Size: {os.path.getsize(font_path)} bytes")
                    break
        
        # Clean up zip file
        os.remove(zip_path)
        print(f"🗑️  Cleaned up: {zip_path}")
        print()
        
        # Clean up extracted folder
        extracted_folder = 'fonts/dejavu-fonts-ttf-2.37'
        if os.path.exists(extracted_folder):
            import shutil
            shutil.rmtree(extracted_folder)
            print(f"🗑️  Cleaned up: {extracted_folder}")
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
        print("1. Download: https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip")
        print("2. Extract DejaVuSans.ttf")
        print("3. Copy to: fonts/DejaVuSans.ttf")
        print()
        return False

if __name__ == "__main__":
    success = download_dejavu_font()
    
    if success:
        print("🎉 Ready to generate bilingual PDFs!")
    else:
        print("⚠️  Please install font manually")
