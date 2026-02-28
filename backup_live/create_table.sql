-- Run this in Supabase SQL Editor
-- Go to: supabase.com → Your Project → SQL Editor → New Query

-- Create emergencies table if not exists
CREATE TABLE IF NOT EXISTS emergencies (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  username TEXT,
  lat FLOAT8 NOT NULL,
  lon FLOAT8 NOT NULL,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'pending'
);

-- Create reminders table if not exists
CREATE TABLE IF NOT EXISTS reminders (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  username TEXT,
  medicine_name TEXT NOT NULL,
  time TEXT NOT NULL,
  dosage TEXT,
  active BOOLEAN DEFAULT true,
  created TIMESTAMPTZ DEFAULT NOW()
);

-- Create appointments table if not exists
CREATE TABLE IF NOT EXISTS appointments (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  username TEXT,
  hospital TEXT NOT NULL,
  date TEXT NOT NULL,
  time TEXT NOT NULL,
  notes TEXT,
  reminder_sent BOOLEAN DEFAULT false,
  created TIMESTAMPTZ DEFAULT NOW()
);

-- Create maternal table if not exists
CREATE TABLE IF NOT EXISTS maternal (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  username TEXT,
  lmp_date TEXT NOT NULL,
  weeks_pregnant INT,
  due_date TEXT,
  created TIMESTAMPTZ DEFAULT NOW()
);

-- Create health_workers table if not exists
CREATE TABLE IF NOT EXISTS health_workers (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  username TEXT,
  name TEXT NOT NULL,
  age INT,
  category TEXT NOT NULL,
  experience INT,
  lat FLOAT8,
  lon FLOAT8,
  approved BOOLEAN DEFAULT false,
  created TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_emergencies_timestamp ON emergencies(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_emergencies_status ON emergencies(status);
CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_active ON reminders(active);
CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
CREATE INDEX IF NOT EXISTS idx_maternal_user_id ON maternal(user_id);
CREATE INDEX IF NOT EXISTS idx_health_workers_user_id ON health_workers(user_id);
CREATE INDEX IF NOT EXISTS idx_health_workers_approved ON health_workers(approved);

-- Enable Row Level Security
ALTER TABLE emergencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE maternal ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_workers ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Allow public inserts" ON emergencies;
DROP POLICY IF EXISTS "Allow public reads" ON emergencies;
DROP POLICY IF EXISTS "Allow public updates" ON emergencies;
DROP POLICY IF EXISTS "Allow public inserts on reminders" ON reminders;
DROP POLICY IF EXISTS "Allow public reads on reminders" ON reminders;
DROP POLICY IF EXISTS "Allow public updates on reminders" ON reminders;
DROP POLICY IF EXISTS "Allow public deletes on reminders" ON reminders;
DROP POLICY IF EXISTS "Allow public inserts on appointments" ON appointments;
DROP POLICY IF EXISTS "Allow public reads on appointments" ON appointments;
DROP POLICY IF EXISTS "Allow public updates on appointments" ON appointments;
DROP POLICY IF EXISTS "Allow public deletes on appointments" ON appointments;
DROP POLICY IF EXISTS "Allow public inserts on maternal" ON maternal;
DROP POLICY IF EXISTS "Allow public reads on maternal" ON maternal;
DROP POLICY IF EXISTS "Allow public updates on maternal" ON maternal;
DROP POLICY IF EXISTS "Allow public inserts on health_workers" ON health_workers;
DROP POLICY IF EXISTS "Allow public reads on health_workers" ON health_workers;
DROP POLICY IF EXISTS "Allow public updates on health_workers" ON health_workers;

-- Create policies for emergencies
CREATE POLICY "Allow public inserts" ON emergencies
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public reads" ON emergencies
  FOR SELECT
  USING (true);

CREATE POLICY "Allow public updates" ON emergencies
  FOR UPDATE
  USING (true);

-- Create policies for reminders
CREATE POLICY "Allow public inserts on reminders" ON reminders
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public reads on reminders" ON reminders
  FOR SELECT
  USING (true);

CREATE POLICY "Allow public updates on reminders" ON reminders
  FOR UPDATE
  USING (true);

CREATE POLICY "Allow public deletes on reminders" ON reminders
  FOR DELETE
  USING (true);

-- Create policies for appointments
CREATE POLICY "Allow public inserts on appointments" ON appointments
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public reads on appointments" ON appointments
  FOR SELECT
  USING (true);

CREATE POLICY "Allow public updates on appointments" ON appointments
  FOR UPDATE
  USING (true);

CREATE POLICY "Allow public deletes on appointments" ON appointments
  FOR DELETE
  USING (true);

-- Create policies for maternal
CREATE POLICY "Allow public inserts on maternal" ON maternal
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public reads on maternal" ON maternal
  FOR SELECT
  USING (true);

CREATE POLICY "Allow public updates on maternal" ON maternal
  FOR UPDATE
  USING (true);

-- Create policies for health_workers
CREATE POLICY "Allow public inserts on health_workers" ON health_workers
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public reads on health_workers" ON health_workers
  FOR SELECT
  USING (true);

CREATE POLICY "Allow public updates on health_workers" ON health_workers
  FOR UPDATE
  USING (true);

-- Create govt_schemes table for government schemes CRUD
CREATE TABLE IF NOT EXISTS govt_schemes (
  id BIGSERIAL PRIMARY KEY,
  title_en TEXT NOT NULL,
  title_hi TEXT,
  title_gu TEXT,
  desc_en TEXT NOT NULL,
  desc_hi TEXT,
  desc_gu TEXT,
  phone TEXT,
  link TEXT,
  active BOOLEAN DEFAULT true,
  created TIMESTAMPTZ DEFAULT NOW()
);

-- Create issues table for problem reporting
CREATE TABLE IF NOT EXISTS issues (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  username TEXT,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  age INT,
  description TEXT NOT NULL,
  status TEXT DEFAULT 'open',
  created TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for new tables
CREATE INDEX IF NOT EXISTS idx_govt_schemes_active ON govt_schemes(active);
CREATE INDEX IF NOT EXISTS idx_issues_user_id ON issues(user_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_created ON issues(created DESC);

-- Enable Row Level Security for new tables
ALTER TABLE govt_schemes ENABLE ROW LEVEL SECURITY;
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow public inserts on govt_schemes" ON govt_schemes;
DROP POLICY IF EXISTS "Allow public reads on govt_schemes" ON govt_schemes;
DROP POLICY IF EXISTS "Allow public updates on govt_schemes" ON govt_schemes;
DROP POLICY IF EXISTS "Allow public deletes on govt_schemes" ON govt_schemes;
DROP POLICY IF EXISTS "Allow public inserts on issues" ON issues;
DROP POLICY IF EXISTS "Allow public reads on issues" ON issues;
DROP POLICY IF EXISTS "Allow public updates on issues" ON issues;

-- Create policies for govt_schemes
CREATE POLICY "Allow public inserts on govt_schemes" ON govt_schemes
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public reads on govt_schemes" ON govt_schemes
  FOR SELECT
  USING (true);

CREATE POLICY "Allow public updates on govt_schemes" ON govt_schemes
  FOR UPDATE
  USING (true);

CREATE POLICY "Allow public deletes on govt_schemes" ON govt_schemes
  FOR DELETE
  USING (true);

-- Create policies for issues
CREATE POLICY "Allow public inserts on issues" ON issues
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Allow public reads on issues" ON issues
  FOR SELECT
  USING (true);

CREATE POLICY "Allow public updates on issues" ON issues
  FOR UPDATE
  USING (true);
