# Appointment Feature Implementation Plan

## Overview
Implement a complete appointment booking system with:
- Patient booking (with doctor selection and date selection)
- Doctor notifications and management
- Dashboard calendar view
- Cancellation by both parties
- Reminder system

## Database Schema ✅ DONE
- Table: `appointments`
- Unique constraint: one appointment per doctor per day
- Status: scheduled, completed, cancelled_by_patient, cancelled_by_doctor

## Implementation Parts

### Part 1: Patient Bot (bot.py)
**Location**: Lines 1136-1160 (existing appointment handlers)

**Changes Needed**:

1. **new_appointment handler** (line 1136):
   - Fetch list of active doctors from database
   - Show doctor selection buttons
   - Store selected doctor in context
   - Show next 10 days as date buttons
   - Check if date is available for selected doctor
   - Ask for reason/notes
   - Create appointment in database
   - Send notification to doctor

2. **list_appointments handler** (line 1141):
   - Query appointments table for patient's appointments
   - Filter by status='scheduled'
   - Show list with doctor name, date, reason
   - Add "Cancel" button for each appointment

3. **cancel_appointment handler**:
   - Show list of patient's scheduled appointments
   - Patient selects which to cancel
   - Update status to 'cancelled_by_patient'
   - Notify doctor

**Flow**:
```
Patient clicks "Book New Visit"
  ↓
Show list of doctors (from doctors table where active=true)
  ↓
Patient selects doctor
  ↓
Show next 10 days as date buttons
  ↓
Patient selects date
  ↓
Check if doctor available on that date
  ↓
If available: Ask for reason
  ↓
Create appointment in database
  ↓
Send notification to doctor bot
  ↓
Confirm to patient
```

### Part 2: Doctor Bot (doctor_bot.py)
**Location**: Main menu + new handlers

**Changes Needed**:

1. **Add "Appointments" button to main menu** (line ~996):
   ```python
   [InlineKeyboardButton("📅 Appointments", callback_data="appointments")]
   ```

2. **appointments handler**:
   - Show upcoming appointments for this doctor
   - Group by date
   - Show patient name, reason
   - Add "Cancel" button for each

3. **Appointment notification**:
   - When patient books appointment
   - Send message to doctor: "New appointment booked!"
   - Show patient details, date, reason
   - Add "View Appointments" button

4. **Cancel appointment**:
   - Doctor can cancel any scheduled appointment
   - Update status to 'cancelled_by_doctor'
   - Notify patient

### Part 3: Dashboard (Streamlit)
**Location**: New page `dashboard/pages/14_📅_Appointments.py`

**Features**:

1. **Calendar Grid View**:
   - Show current month in grid format
   - Each cell = one day
   - Highlight dates with appointments
   - Show patient name in cell
   - Color code by status (scheduled=green, completed=blue, cancelled=red)

2. **Filters**:
   - Filter by doctor
   - Filter by month
   - Filter by status

3. **Appointment Details**:
   - Click on date to see full details
   - Patient info, doctor info, reason
   - Status
   - Actions: Mark as completed, Cancel

4. **Statistics**:
   - Total appointments this month
   - By doctor
   - By status

### Part 4: Reminder System
**Location**: New file `appointment_reminder.py`

**Features**:
- Cron job or scheduled task
- Run daily at 9 AM
- Check appointments for tomorrow
- Send reminder to patients
- Mark reminder_sent=true

**Implementation**:
```python
# Check appointments for tomorrow
tomorrow = (datetime.now() + timedelta(days=1)).date()
appointments = get_appointments_for_date(tomorrow, reminder_sent=False)

for apt in appointments:
    send_reminder_to_patient(apt)
    mark_reminder_sent(apt.id)
```

## Implementation Order

1. ✅ Database schema created
2. 🔄 Patient bot - booking flow
3. 🔄 Doctor bot - appointments view
4. 🔄 Dashboard - calendar page
5. 🔄 Reminder system

## Testing Checklist

- [ ] Patient can see list of doctors
- [ ] Patient can select doctor
- [ ] Patient can see next 10 days
- [ ] Patient can select available date
- [ ] System prevents double booking
- [ ] Appointment is created in database
- [ ] Doctor receives notification
- [ ] Doctor can view appointments
- [ ] Patient can view their appointments
- [ ] Patient can cancel appointment
- [ ] Doctor can cancel appointment
- [ ] Dashboard shows calendar correctly
- [ ] Dashboard highlights booked dates
- [ ] Reminder is sent 1 day before
- [ ] Reminder is sent only once

## Files to Modify

1. `bot.py` - Patient appointment booking
2. `doctor_bot.py` - Doctor appointments view
3. `dashboard/pages/14_📅_Appointments.py` - NEW FILE
4. `appointment_reminder.py` - NEW FILE (optional, for automated reminders)

## Estimated Lines of Code

- Patient bot: ~200 lines
- Doctor bot: ~150 lines
- Dashboard: ~300 lines
- Reminder: ~100 lines
- Total: ~750 lines

This is a significant feature! Should I proceed with implementation?
