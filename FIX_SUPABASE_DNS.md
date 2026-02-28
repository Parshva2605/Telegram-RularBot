# Fix Supabase Connection in India - DNS Setup Guide

## Problem
Supabase is blocked by Indian ISPs since Feb 24, 2026. Your bot can't connect to database.

## Solution: Change DNS to Cloudflare (Permanent Fix)

---

## METHOD 1: Windows GUI (Recommended for Long-term)

### Step 1: Open Network Settings
1. Press `Win + R`
2. Type: `ncpa.cpl`
3. Press Enter

### Step 2: Configure DNS
1. Right-click your active network (Wi-Fi or Ethernet)
2. Click "Properties"
3. Double-click "Internet Protocol Version 4 (TCP/IPv4)"
4. Select "Use the following DNS server addresses"
5. Enter:
   - **Preferred DNS**: `1.1.1.1` (Cloudflare Primary)
   - **Alternate DNS**: `1.0.0.1` (Cloudflare Secondary)
6. Click "OK" → "OK"

### Step 3: Flush DNS Cache
Open PowerShell as Administrator and run:
```powershell
ipconfig /flushdns
```

### Step 4: Test Connection
```bash
python test_supabase_key.py
```

---

## METHOD 2: PowerShell Command (Quick)

Run PowerShell as Administrator:

```powershell
# Get your network adapter name
Get-NetAdapter | Where-Object {$_.Status -eq "Up"}

# Set DNS (replace "Wi-Fi" with your adapter name)
Set-DnsClientServerAddress -InterfaceAlias "Wi-Fi" -ServerAddresses ("1.1.1.1","1.0.0.1")

# Flush DNS
ipconfig /flushdns

# Verify
Get-DnsClientServerAddress -InterfaceAlias "Wi-Fi"
```

---

## METHOD 3: Router-Level DNS (Best for Multiple Devices)

1. Open router admin panel (usually http://192.168.1.1 or http://192.168.0.1)
2. Login with admin credentials
3. Find "DNS Settings" or "WAN Settings"
4. Set Primary DNS: `1.1.1.1`
5. Set Secondary DNS: `1.0.0.1`
6. Save and restart router
7. Restart your computer

**Advantage**: All devices on your network will bypass the block

---

## ALTERNATIVE DNS PROVIDERS

If Cloudflare doesn't work, try:

### Google DNS
- Primary: `8.8.8.8`
- Secondary: `8.8.4.4`

### Quad9 DNS
- Primary: `9.9.9.9`
- Secondary: `149.112.112.112`

---

## VERIFY IT'S WORKING

After changing DNS, test:

```bash
# Test 1: DNS resolution
nslookup hpflwfpbloifbarekyrn.supabase.co

# Test 2: Connection
curl https://hpflwfpbloifbarekyrn.supabase.co

# Test 3: Supabase key
python test_supabase_key.py

# Test 4: Doctor bot
python doctor_bot.py
```

You should see:
- ✅ Supabase connected!
- ✅ Query successful!

---

## TROUBLESHOOTING

### Still not working?

**Option A: Use VPN**
- Install ProtonVPN, Windscribe, or any VPN
- Connect to server outside India
- Run bot

**Option B: Mobile Hotspot**
- Use mobile data (Jio/Airtel 4G/5G)
- Mobile networks may not have the block
- Connect PC to mobile hotspot

**Option C: Custom Domain (Advanced)**
- Set up custom domain in Supabase
- Point to your project
- Costs extra but bypasses ISP blocks

---

## LONG-TERM RECOMMENDATION

**Best Setup for Production:**

1. **Change DNS to Cloudflare** (1.1.1.1) - Free, fast, reliable
2. **Keep VPN as backup** - In case DNS doesn't work
3. **Monitor Supabase status**: https://status.supabase.com
4. **Consider custom domain** if block persists for months

---

## AFTER DNS CHANGE

Once DNS is working:

1. Run `python doctor_bot.py` - Should connect to Supabase
2. Run `python bot.py` - Should connect to Supabase
3. Test dashboard: `streamlit run dashboard/app.py`
4. All database features will work automatically

---

## NOTES

- DNS change is **permanent** until you change it back
- Cloudflare DNS (1.1.1.1) is **faster** than most ISP DNS
- This fix works for **all Supabase projects**, not just yours
- No code changes needed - just DNS configuration

---

## SUPPORT

If still having issues:
1. Check Supabase status: https://status.supabase.com
2. Try different DNS provider (Google 8.8.8.8)
3. Use VPN as temporary solution
4. Contact your ISP to report the block
