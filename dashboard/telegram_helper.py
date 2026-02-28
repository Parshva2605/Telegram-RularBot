# -*- coding: utf-8 -*-
"""
Telegram Helper for Admin Panel
Send messages and reminders to doctors via Telegram bot
"""

import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

# Try multiple paths to find .env.doctor
possible_paths = [
    '.env.doctor',                                    # Current directory
    '../.env.doctor',                                 # Parent directory
    os.path.join(os.path.dirname(__file__), '..', '.env.doctor'),  # Relative to this file
    os.path.join(os.getcwd(), '.env.doctor'),        # Working directory
    os.path.join(os.getcwd(), '..', '.env.doctor'),  # Parent of working directory
]

# Try loading from each path
loaded = False
for path in possible_paths:
    if os.path.exists(path):
        load_dotenv(path)
        print(f"✅ Loaded environment from: {path}")
        loaded = True
        break

if not loaded:
    print("⚠️ Warning: .env.doctor file not found in any expected location")
    print(f"Searched paths: {possible_paths}")

MEDIMIND_DOCTOR_TOKEN = os.getenv("MEDIMIND_DOCTOR_TOKEN")

# Debug: Print token status
if MEDIMIND_DOCTOR_TOKEN:
    print(f"✅ Doctor bot token loaded: {MEDIMIND_DOCTOR_TOKEN[:20]}...")
else:
    print("❌ MEDIMIND_DOCTOR_TOKEN not found!")
    print("Please ensure .env.doctor file exists with MEDIMIND_DOCTOR_TOKEN set")

async def send_reminder_to_doctor(doctor_telegram_id: int, request_id: int, patient_name: str, waiting_hours: int, patient_age: int = None, patient_village: str = None):
    """
    Send reminder to doctor about pending X-ray request
    
    Args:
        doctor_telegram_id: Doctor's Telegram user ID
        request_id: X-ray request ID
        patient_name: Patient's name
        waiting_hours: Hours the request has been waiting
        patient_age: Patient's age (optional)
        patient_village: Patient's village (optional)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Check if token is available
        if not MEDIMIND_DOCTOR_TOKEN:
            print("❌ ERROR: MEDIMIND_DOCTOR_TOKEN is not set!")
            print("Please check your .env.doctor file")
            return False
        
        bot = Bot(token=MEDIMIND_DOCTOR_TOKEN)
        
        # Build patient info
        patient_info = f"👤 Patient: {patient_name}"
        if patient_age:
            patient_info += f" ({patient_age}y)"
        if patient_village:
            patient_info += f" - {patient_village}"
        
        message = (
            f"🔔 **URGENT REMINDER**\n\n"
            f"📋 Request #{request_id} is PENDING\n"
            f"{patient_info}\n"
            f"⏰ Waiting: {waiting_hours} hours\n\n"
            f"⚠️ **Please complete this X-ray analysis immediately!**\n\n"
            f"👉 Click 'Requests' button below to analyze now."
        )
        
        await bot.send_message(
            chat_id=doctor_telegram_id,
            text=message,
            parse_mode='Markdown'
        )
        
        print(f"✅ Reminder sent successfully to doctor {doctor_telegram_id}")
        return True
    
    except Exception as e:
        print(f"❌ Error sending reminder: {e}")
        return False

async def send_custom_message_to_doctor(doctor_telegram_id: int, message_text: str, request_id: int = None):
    """
    Send custom message to doctor
    
    Args:
        doctor_telegram_id: Doctor's Telegram user ID
        message_text: Custom message text
        request_id: Optional request ID for context
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        bot = Bot(token=MEDIMIND_DOCTOR_TOKEN)
        
        if request_id:
            full_message = (
                f"💬 **Message from Admin**\n\n"
                f"📋 Regarding Request #{request_id}\n\n"
                f"{message_text}"
            )
        else:
            full_message = (
                f"💬 **Message from Admin**\n\n"
                f"{message_text}"
            )
        
        await bot.send_message(
            chat_id=doctor_telegram_id,
            text=full_message,
            parse_mode='Markdown'
        )
        
        return True
    
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

async def send_bulk_reminders(doctor_requests: list):
    """
    Send reminders to multiple doctors
    
    Args:
        doctor_requests: List of dicts with doctor_telegram_id, request_id, patient_name, waiting_hours, patient_age, patient_village
    
    Returns:
        dict: Success and failure counts
    """
    success_count = 0
    failure_count = 0
    
    for dr in doctor_requests:
        result = await send_reminder_to_doctor(
            dr['doctor_telegram_id'],
            dr['request_id'],
            dr['patient_name'],
            dr['waiting_hours'],
            dr.get('patient_age'),
            dr.get('patient_village')
        )
        
        if result:
            success_count += 1
        else:
            failure_count += 1
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)
    
    return {
        'success': success_count,
        'failure': failure_count
    }

# Synchronous wrappers for Streamlit
def send_reminder_sync(doctor_telegram_id: int, request_id: int, patient_name: str, waiting_hours: int, patient_age: int = None, patient_village: str = None):
    """Synchronous wrapper for send_reminder_to_doctor"""
    return asyncio.run(send_reminder_to_doctor(doctor_telegram_id, request_id, patient_name, waiting_hours, patient_age, patient_village))

def send_message_sync(doctor_telegram_id: int, message_text: str, request_id: int = None):
    """Synchronous wrapper for send_custom_message_to_doctor"""
    return asyncio.run(send_custom_message_to_doctor(doctor_telegram_id, message_text, request_id))

def send_bulk_reminders_sync(doctor_requests: list):
    """Synchronous wrapper for send_bulk_reminders"""
    return asyncio.run(send_bulk_reminders(doctor_requests))

# Test function
if __name__ == "__main__":
    # Test sending a reminder
    test_telegram_id = 123456789  # Replace with actual telegram ID
    test_request_id = 1
    test_patient_name = "Test Patient"
    test_waiting_hours = 24
    
    print("Testing reminder send...")
    result = send_reminder_sync(test_telegram_id, test_request_id, test_patient_name, test_waiting_hours)
    print(f"Result: {'Success' if result else 'Failed'}")
