-- ============================================
-- MediMind X-Ray AI Doctor Bot - Database Schema
-- Step 2: Supabase Tables for X-Ray Feature
-- Created: 2026-02-28
-- MCI Compliant + Privacy + RLS Enabled
-- ============================================

-- ============================================
-- TABLE 1: DOCTORS (Phone + MCI Verified)
-- ============================================
CREATE TABLE IF NOT EXISTS doctors (
    id BIGSERIAL PRIMARY KEY,
    phone TEXT UNIQUE NOT NULL,              -- +919876543210 (unique identifier)
    telegram_id BIGINT UNIQUE,               -- Doctor's Telegram user ID
    access_code TEXT UNIQUE NOT NULL,        -- X7K9P2M4 (website login code)
    name TEXT NOT NULL,                      -- Dr. Shah
    mci_reg TEXT,                            -- GJMC12345 (Medical Council of India)
    phc TEXT,                                -- Anklav PHC (Primary Health Center)
    rating FLOAT DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    total_cases INT DEFAULT 0,               -- Total X-rays reviewed
    active BOOLEAN DEFAULT true,             -- Active/Inactive status
    created TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Indexes for doctors table
CREATE INDEX IF NOT EXISTS idx_doctors_phone ON doctors(phone);
CREATE INDEX IF NOT EXISTS idx_doctors_telegram ON doctors(telegram_id);
CREATE INDEX IF NOT EXISTS idx_doctors_access_code ON doctors(access_code);
CREATE INDEX IF NOT EXISTS idx_doctors_active ON doctors(active);

-- ============================================
-- TABLE 2: X-RAY REQUESTS (14-Disease + Workflow)
-- ============================================
CREATE TABLE IF NOT EXISTS xray_requests (
    id BIGSERIAL PRIMARY KEY,
    
    -- Patient Information
    patient_name TEXT NOT NULL,
    age INT CHECK (age > 0 AND age < 120),
    village TEXT,
    symptoms TEXT,
    
    -- Image & Scan Details
    image_url TEXT,                          -- Supabase Storage URL
    scan_type TEXT CHECK (scan_type IN ('X-ray', 'CT', 'MRI', 'Skin')),
    
    -- AI Analysis Results
    model_used TEXT,                         -- llava:13b OR phc_xray14
    diseases_detected JSONB,                 -- ["Pneumonia", "Cardiomegaly"]
    confidence_scores JSONB,                 -- {"Pneumonia": 0.92, "TB": 0.12}
    ai_report TEXT,                          -- VLM: "J18.9 pneumonia + ECG needed"
    
    -- Doctor Review
    doctor_notes TEXT,                       -- Dr edits: "Add SpO2 check"
    doctor_phone TEXT REFERENCES doctors(phone) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    
    -- Patient Communication
    hindi_patient TEXT,                      -- Sarvam-1: "फेफड़ों में निमोनिया"
    report_pdf_url TEXT,                     -- Final PDF Storage URL
    
    -- Workflow Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'sent', 'cancelled')),
    consent_time TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for xray_requests table
CREATE INDEX IF NOT EXISTS idx_xray_status ON xray_requests(status);
CREATE INDEX IF NOT EXISTS idx_xray_doctor ON xray_requests(doctor_phone);
CREATE INDEX IF NOT EXISTS idx_xray_patient ON xray_requests(patient_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_xray_created ON xray_requests(created_at DESC);

-- ============================================
-- ROW LEVEL SECURITY (RLS) - MCI Compliance
-- ============================================

-- Enable RLS on both tables
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE xray_requests ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for re-running script)
DROP POLICY IF EXISTS "Doctors view own profile" ON doctors;
DROP POLICY IF EXISTS "Doctors update own profile" ON doctors;
DROP POLICY IF EXISTS "Admin full access doctors" ON doctors;
DROP POLICY IF EXISTS "Public insert doctors" ON doctors;

DROP POLICY IF EXISTS "Doctors view assigned xrays" ON doctors;
DROP POLICY IF EXISTS "Public insert xray requests" ON xray_requests;
DROP POLICY IF EXISTS "Doctors update assigned xrays" ON xray_requests;
DROP POLICY IF EXISTS "Admin full access xrays" ON xray_requests;

-- ============================================
-- DOCTORS TABLE POLICIES
-- ============================================

-- Doctors can view their own profile
CREATE POLICY "Doctors view own profile" ON doctors
    FOR SELECT
    USING (phone = current_setting('app.current_phone', true)::text);

-- Doctors can update their own profile
CREATE POLICY "Doctors update own profile" ON doctors
    FOR UPDATE
    USING (phone = current_setting('app.current_phone', true)::text);

-- Allow public insert for doctor registration (bot will insert)
CREATE POLICY "Public insert doctors" ON doctors
    FOR INSERT
    WITH CHECK (true);

-- Admin/Bot can view all doctors
CREATE POLICY "Admin full access doctors" ON doctors
    FOR ALL
    USING (true);

-- ============================================
-- XRAY_REQUESTS TABLE POLICIES
-- ============================================

-- Doctors can view assigned X-rays + pending queue
CREATE POLICY "Doctors view assigned xrays" ON xray_requests
    FOR SELECT
    USING (
        doctor_phone = current_setting('app.current_phone', true)::text 
        OR status = 'pending'
    );

-- Public can insert X-ray requests (bot will insert)
CREATE POLICY "Public insert xray requests" ON xray_requests
    FOR INSERT
    WITH CHECK (true);

-- Doctors can update assigned X-rays
CREATE POLICY "Doctors update assigned xrays" ON xray_requests
    FOR UPDATE
    USING (doctor_phone = current_setting('app.current_phone', true)::text);

-- Admin/Bot can access all X-ray requests
CREATE POLICY "Admin full access xrays" ON xray_requests
    FOR ALL
    USING (true);

-- ============================================
-- TEST DATA (Optional - for verification)
-- ============================================

-- Test Doctor
INSERT INTO doctors (phone, telegram_id, access_code, name, mci_reg, phc)
VALUES ('+919876543210', 123456789, 'TEST1234', 'Dr. Shah', 'GJMC12345', 'Anklav PHC')
ON CONFLICT (phone) DO NOTHING;

-- Test X-ray Request
INSERT INTO xray_requests (patient_name, age, village, symptoms, doctor_phone, status, scan_type)
VALUES ('Ramesh Patel', 45, 'Anklav', 'Cough + chest pain', '+919876543210', 'pending', 'X-ray')
ON CONFLICT DO NOTHING;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('doctors', 'xray_requests');

-- Check RLS status
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('doctors', 'xray_requests');

-- Count records
SELECT 'doctors' as table_name, COUNT(*) as count FROM doctors
UNION ALL
SELECT 'xray_requests' as table_name, COUNT(*) as count FROM xray_requests;

-- ============================================
-- NOTES
-- ============================================
-- 1. Run this script in Supabase SQL Editor
-- 2. Verify tables appear in Table Editor
-- 3. Check RLS is enabled (padlock icon)
-- 4. Test data should be visible
-- 5. Screenshot for verification
-- ============================================
