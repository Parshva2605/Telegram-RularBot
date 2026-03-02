# Appointments Feature Setup

## Step 1: Create Appointments Table

1. Go to your Supabase project dashboard
2. Click on "SQL Editor" in the left sidebar
3. Click "New Query"
4. Copy and paste the contents of `create_appointments_table.sql`
5. Click "Run" to execute

## Step 2: Verify Table Creation

Run this query to verify:

```sql
SELECT * FROM appointments LIMIT 1;
```

You should see the table structure with no errors.

## Step 3: Enable Row Level Security (Optional)

If you want to enable RLS for security:

```sql
-- Enable RLS
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations (since we're using service key)
CREATE POLICY "Allow all operations" ON appointments
FOR ALL
USING (true)
WITH CHECK (true);
```

## Step 4: Test Insert

Test that the unique constraint works:

```sql
-- This should work
INSERT INTO appointments (
  patient_telegram_id, 
  patient_name, 
  doctor_phone, 
  doctor_name, 
  appointment_date, 
  reason
) VALUES (
  1234567890, 
  'Test Patient', 
  '+919638622240', 
  'Dr. A', 
  '2026-03-10', 
  'Regular checkup'
);

-- This should fail (duplicate doctor + date)
INSERT INTO appointments (
  patient_telegram_id, 
  patient_name, 
  doctor_phone, 
  doctor_name, 
  appointment_date, 
  reason
) VALUES (
  9876543210, 
  'Another Patient', 
  '+919638622240', 
  'Dr. A', 
  '2026-03-10', 
  'Consultation'
);
```

The second insert should fail with a unique constraint violation.

## Step 5: Clean Up Test Data

```sql
DELETE FROM appointments WHERE patient_name = 'Test Patient';
```

## Features Implemented

✅ One appointment per doctor per day
✅ Patient can book appointments
✅ Patient can cancel appointments
✅ Doctor can cancel appointments
✅ Reminder system (1 day before)
✅ Calendar view in dashboard
✅ Appointment notifications

## Database Schema

- `id`: Unique appointment ID
- `patient_telegram_id`: Patient's Telegram ID
- `patient_name`: Patient's name
- `patient_phone`: Patient's phone (optional)
- `patient_village`: Patient's village
- `doctor_phone`: Doctor's phone (unique with date)
- `doctor_name`: Doctor's name
- `doctor_phc`: Doctor's PHC
- `appointment_date`: Date of appointment (unique with doctor)
- `reason`: Reason for appointment
- `status`: scheduled, completed, cancelled_by_patient, cancelled_by_doctor
- `created_at`: When appointment was created
- `updated_at`: Last update time
- `reminder_sent`: Whether reminder was sent

## Next Steps

After creating the table:
1. Restart patient bot: `python bot.py`
2. Restart doctor bot: `python doctor_bot.py`
3. Restart dashboard: `streamlit run dashboard/app.py`

The appointment feature will be available in:
- Patient bot: My Planner → Appointments
- Doctor bot: Main menu → Appointments
- Dashboard: New "Appointments" page
