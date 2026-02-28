-- ============================================
-- INSERT/UPDATE TEST DOCTOR FOR DASHBOARD LOGIN
-- Run this in Supabase SQL Editor
-- ============================================

-- First, check what doctors exist
SELECT phone, access_code, name, phc, active FROM doctors ORDER BY phone;

-- ============================================
-- OPTION 1: Update existing test doctor
-- ============================================
UPDATE doctors 
SET access_code = 'TEST1234',
    name = 'Dr. Test Kumar',
    mci_reg = 'TEST12345',
    phc = 'Test PHC',
    active = true
WHERE phone = '+919999999999';

-- ============================================
-- OPTION 2: Insert new test doctor (if doesn't exist)
-- ============================================
INSERT INTO doctors (
    phone, 
    telegram_id, 
    access_code, 
    name, 
    mci_reg, 
    phc, 
    rating, 
    total_cases, 
    active
)
VALUES (
    '+919999999999',           -- Phone number for login
    999999999,                 -- Telegram ID (dummy)
    'TEST1234',                -- Access code for login
    'Dr. Test Kumar',          -- Doctor name
    'TEST12345',               -- MCI Registration
    'Test PHC',                -- PHC name
    5.0,                       -- Rating
    0,                         -- Total cases
    true                       -- Active status
)
ON CONFLICT (phone) DO UPDATE SET
    access_code = 'TEST1234',
    name = 'Dr. Test Kumar',
    mci_reg = 'TEST12345',
    phc = 'Test PHC',
    active = true;

-- ============================================
-- Verify the test doctor exists
-- ============================================
SELECT 
    phone, 
    access_code, 
    name, 
    phc, 
    mci_reg,
    active,
    rating,
    total_cases
FROM doctors 
WHERE phone IN ('+919999999999', '+919876543210')
ORDER BY phone;

-- ============================================
-- READY TO USE CREDENTIALS
-- ============================================
-- After running this SQL, you can login with:
--
-- OPTION 1 (Recommended - Already exists):
-- Phone: +919876543210
-- Access Code: TEST1234
-- Name: Dr. Shah
--
-- OPTION 2 (Test doctor):
-- Phone: +919999999999
-- Access Code: TEST1234
-- Name: Dr. Test Kumar
-- ============================================

-- ============================================
-- TROUBLESHOOTING
-- ============================================
-- If login still fails, check the actual access code:
SELECT phone, access_code, name FROM doctors WHERE phone = '+919876543210';

-- If you want to set a custom access code:
-- UPDATE doctors SET access_code = 'MYCODE123' WHERE phone = '+919876543210';
-- ============================================
