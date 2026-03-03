import os
from dotenv import load_dotenv
from supabase_wrapper import create_client

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("=== CHECKING APPOINTMENTS WITH DETAILS ===\n")

# Get appointments
appointments = supabase.table('appointments').select('*').execute()
print(f"Total appointments: {len(appointments.data)}\n")

# Get doctors
doctors = supabase.table('doctors').select('*').execute()
print(f"Total doctors: {len(doctors.data)}\n")

# Create doctor mapping
doctors_dict = {d['phone']: d for d in doctors.data}

print("=== APPOINTMENTS ===")
for apt in appointments.data:
    print(f"\nID: {apt['id']}")
    print(f"Patient: {apt['patient_name']}")
    print(f"Doctor Phone: {apt['doctor_phone']}")
    
    # Check if doctor exists
    if apt['doctor_phone'] in doctors_dict:
        doctor = doctors_dict[apt['doctor_phone']]
        print(f"Doctor Name: {doctor['name']}")
        print(f"Doctor PHC: {doctor.get('phc', 'N/A')}")
    else:
        print(f"Doctor Name: NOT FOUND IN DOCTORS TABLE")
    
    print(f"Date: {apt['appointment_date']}")
    print(f"Status: {apt['status']}")
    print(f"Reason: {apt.get('reason', 'N/A')}")
    print(f"Created At: {apt.get('created_at', 'N/A')}")
    print(f"Patient Phone: {apt.get('patient_phone', 'N/A')}")
    print(f"Patient Village: {apt.get('patient_village', 'N/A')}")
    print("-" * 50)
