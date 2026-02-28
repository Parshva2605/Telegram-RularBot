import os
from dotenv import load_dotenv

load_dotenv('dashboard/.env')
key = os.getenv('SUPABASE_KEY')

print(f"Key: {key}")
print(f"Key prefix: {key[:20]}")

if key.startswith('sb_secret_'):
    print("✅ This is a SERVICE_ROLE key (should bypass RLS)")
elif key.startswith('eyJ'):
    print("⚠️  This is an ANON key (RLS enforced)")
else:
    print("❓ Unknown key type")
