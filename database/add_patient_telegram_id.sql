-- Add patient_telegram_id field to xray_requests table
-- Run this in Supabase SQL Editor

-- Add the column if it doesn't exist
ALTER TABLE xray_requests 
ADD COLUMN IF NOT EXISTS patient_telegram_id BIGINT;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_xray_patient_telegram ON xray_requests(patient_telegram_id);

-- Verify the change
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'xray_requests' 
AND column_name = 'patient_telegram_id';
