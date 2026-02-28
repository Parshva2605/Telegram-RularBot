-- ============================================
-- INSERT TEST DOCTOR FOR DASHBOARD LOGIN
-- Run this in Supabase SQL Editor
-- ============================================

-- Update existing test doctor with correct access code
UPDATE doctors 
SET access_code = 'TEST1234',
    name = 'Dr. Test Kumar',
    mci_reg = 'TEST12345',
    phc = 'Test PHC',
    active = true
WHERE phone = '+919999999999';

-- If update didn't work (doctor doesn't exist), insert new one
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

-- Verify the update
SELECT phone, access_code, name, phc FROM doctors WHERE phone = '+919999999999';

-- ============================================
-- ALTERNATIVE: Use existing doctor
-- ============================================
-- You can also use this existing doctor:
-- Phone: +919876543210
-- Access Code: TEST1234
-- Name: Dr. Shah
-- ============================================

-- ============================================
-- LOGIN CREDENTIALS FOR DASHBOARD
-- ============================================
-- Option 1:
-- Phone: +919999999999
-- Access Code: TEST1234
--
-- Option 2 (Already exists):
-- Phone: +919876543210
-- Access Code: TEST1234
-- ============================================
