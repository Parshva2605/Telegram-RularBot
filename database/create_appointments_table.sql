-- Appointments Table for MediMind
-- One appointment per doctor per day

CREATE TABLE IF NOT EXISTS appointments (
  id SERIAL PRIMARY KEY,
  patient_telegram_id BIGINT NOT NULL,
  patient_name TEXT NOT NULL,
  patient_phone TEXT,
  patient_village TEXT,
  doctor_phone TEXT NOT NULL,
  doctor_name TEXT NOT NULL,
  doctor_phc TEXT,
  appointment_date DATE NOT NULL,
  reason TEXT,
  status TEXT DEFAULT 'scheduled', -- scheduled, completed, cancelled_by_patient, cancelled_by_doctor
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  reminder_sent BOOLEAN DEFAULT FALSE,
  
  -- Ensure only one appointment per doctor per day
  UNIQUE(doctor_phone, appointment_date)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_date ON appointments(doctor_phone, appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_telegram_id);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);

-- Comments
COMMENT ON TABLE appointments IS 'Patient appointments with doctors - one per doctor per day';
COMMENT ON COLUMN appointments.status IS 'scheduled, completed, cancelled_by_patient, cancelled_by_doctor';
COMMENT ON COLUMN appointments.reminder_sent IS 'Whether reminder was sent 1 day before appointment';
