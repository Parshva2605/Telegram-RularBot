-- Create doctor_patient_messages table for tracking communication
-- Run this in Supabase SQL Editor (OPTIONAL - for audit trail)

CREATE TABLE IF NOT EXISTS doctor_patient_messages (
    id BIGSERIAL PRIMARY KEY,
    
    -- Request Reference
    request_id BIGINT REFERENCES xray_requests(id) ON DELETE CASCADE,
    
    -- Participants
    doctor_phone TEXT REFERENCES doctors(phone),
    doctor_telegram_id BIGINT,
    patient_telegram_id BIGINT,
    
    -- Message Details
    message_type TEXT CHECK (message_type IN ('voice', 'text')),
    message_text TEXT,              -- Original text (if text message)
    message_text_hindi TEXT,        -- Hindi translation (if text message)
    voice_file_id TEXT,             -- Telegram file_id (if voice message)
    voice_duration INT,             -- Duration in seconds (if voice message)
    
    -- Metadata
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    delivered BOOLEAN DEFAULT true
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_messages_request ON doctor_patient_messages(request_id);
CREATE INDEX IF NOT EXISTS idx_messages_doctor ON doctor_patient_messages(doctor_phone);
CREATE INDEX IF NOT EXISTS idx_messages_patient ON doctor_patient_messages(patient_telegram_id);
CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON doctor_patient_messages(sent_at DESC);

-- Enable Row Level Security
ALTER TABLE doctor_patient_messages ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow public inserts on messages" ON doctor_patient_messages;
DROP POLICY IF EXISTS "Allow public reads on messages" ON doctor_patient_messages;
DROP POLICY IF EXISTS "Doctors view their messages" ON doctor_patient_messages;

-- Create policies
CREATE POLICY "Allow public inserts on messages" ON doctor_patient_messages
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow public reads on messages" ON doctor_patient_messages
    FOR SELECT
    USING (true);

CREATE POLICY "Doctors view their messages" ON doctor_patient_messages
    FOR SELECT
    USING (doctor_phone = current_setting('app.current_phone', true)::text);

-- Verify table creation
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'doctor_patient_messages'
ORDER BY ordinal_position;

-- Show count
SELECT COUNT(*) as total_messages FROM doctor_patient_messages;
