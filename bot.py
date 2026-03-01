# -*- coding: utf-8 -*-
import os
import logging
import requests
import schedule
import threading
import time
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from geopy.distance import geodesic
from supabase_wrapper import create_client
from datetime import datetime

load_dotenv()

# Load doctor bot token for sending notifications
DOCTOR_BOT_TOKEN = os.getenv('MEDIMIND_DOCTOR_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase with debug
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
ADMIN_ID = os.getenv('ADMIN_ID')

print("=== SUPABASE DEBUG ===")
print(f"SUPABASE_URL: {SUPABASE_URL[:30] if SUPABASE_URL else 'NOT SET'}...")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:30] if SUPABASE_KEY else 'NOT SET'}...")
print(f"ADMIN_ID: {ADMIN_ID}")

supabase = None
supabase_connected = False

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test connection
        response = supabase.table('emergencies').select('*', count='exact').execute()
        print(f"✅ Supabase connected! Rows: {response.count}")
        print(f"Response: {response}")
        supabase_connected = True
    else:
        print("❌ Supabase credentials not set in .env")
except Exception as e:
    print(f"❌ Supabase connection error: {e}")
    print("⚠️ Emergency will only send to ADMIN (no database)")
    supabase = None

print("=== SUPABASE DEBUG END ===\n")

TEXTS = {
    'en': {
        'welcome': '🏥 Welcome to MediMind Rural!\n\nSelect your preferred language:',
        'main_menu': '🏥 MediMind Rural - Main Menu\n\nChoose a service:',
        'coming_soon': '⏳ Feature coming soon!',
        'unknown': '❓ Please use the menu buttons or /start command.',
        'hospital_prompt': '📍 Share your location or search by city name:',
        'searching': '🔍 Searching for nearby hospitals...',
        'no_hospitals': '❌ No hospitals found nearby.\n\n🔍 Try: Anand, V.V.Nagar, Anklav',
        'error': '⚠️ Error occurred. Please try again.',
        'disclaimer': '\n\n⚠️ Disclaimer: Please verify details before visiting.',
        'enter_city': '📝 Enter city name (e.g., Anand, V.V.Nagar, Anklav):',
        'hospitals_nearby': '🏥 Hospitals Near You ({}):',
        'search_other': '\n\nSearch other city? Anand/V.V.Nagar',
        'emergency_prompt': '🚨 EMERGENCY HELP\n\nShare your LIVE location for immediate assistance:',
        'sos_sent': '✅ SOS sent! Help is on the way!\n\n📍 Your location: {}',
        'sos_error': '❌ Failed to send SOS. Please try again or call 108.',
        'emergency_cancel': '❌ Emergency request cancelled.',
        'medicine_prompt': '💊 Medicine Reminder Setup\n\nEnter medicine name:',
        'medicine_time': '⏰ What time should I remind you?\n\nFormat: 09:00 AM or 21:30',
        'medicine_dosage': '📋 Dosage/Frequency?\n\nExample: 2 tablets daily, 1 spoon after meal',
        'reminder_set': '✅ Reminder set!\n\n💊 {}\n⏰ {}\n📋 {}\n\nYou will be reminded daily.',
        'reminder_error': '❌ Failed to set reminder. Please try again.',
        'list_reminders': '📋 Your Active Reminders:',
        'no_reminders': '📭 No active reminders.',
        'reminder_stopped': '✅ Reminder deleted successfully.',
        'reminder_notification': '💊 MEDICINE REMINDER!\n\n{}\n📋 {}\n\n⏰ Time to take your medicine!',
        'medicine_menu': '💊 Medicine Reminder\n\nWhat would you like to do?',
        'delete_prompt': '🗑️ Delete Reminder\n\nEnter the number of reminder to delete:',
        'visit_menu': '📅 Visit Planner\n\nWhat would you like to do?',
        'appointment_hospital': '🏥 Enter Doctor/Hospital name:',
        'appointment_date': '📅 Enter date (DD-MM-YYYY):\n\nExample: 23-02-2026',
        'appointment_time': '⏰ Enter time (HH:MM AM/PM):\n\nExample: 10:00 AM',
        'appointment_notes': '📝 Enter notes (optional):\n\nExample: Follow-up BP check',
        'appointment_booked': '✅ Appointment Booked!\n\n🏥 {}\n📅 {}\n⏰ {}\n📝 {}\n\n🔔 You will be reminded 1 day before.',
        'appointment_error': '❌ Failed to book appointment. Please try again.',
        'list_appointments': '📋 Your Upcoming Appointments:',
        'no_appointments': '📭 No upcoming appointments.',
        'appointment_reminder': '🔔 APPOINTMENT REMINDER!\n\nTomorrow at {}\n🏥 {}\n📝 {}\n\nDon\'t forget!',
        'cancel_appointment_prompt': '❌ Cancel Appointment\n\nEnter the number of appointment to cancel:',
        'appointment_cancelled': '✅ Appointment cancelled successfully.',
        'maternal_menu': '👶 Maternal Health\n\nWhat would you like to know?',
        'lmp_prompt': '🤰 Pregnancy Week Calculator\n\nEnter your Last Menstrual Period (LMP) date:\n\nFormat: DD-MM-YYYY\nExample: 01-01-2026',
        'pregnancy_result': '🤰 Pregnancy Information:\n\n📅 LMP: {}\n⏰ Weeks Pregnant: {} weeks\n👶 Due Date: {}\n🏥 Next ANC Visit: {}\n\n💡 Tip: Regular checkups are important!',
        'maternal_error': '❌ Invalid date format. Please use DD-MM-YYYY',
        'schemes_info': '🌿 Gujarat Mother & Child Schemes:\n\n1️⃣ PMMVY (Pradhan Mantri Matru Vandana Yojana)\n💰 ₹5,000 in 3 installments\n📋 For first living child\n\n2️⃣ JSSK (Janani Shishu Suraksha Karyakram)\n🏥 Free delivery in govt hospitals\n💊 Free medicines & diagnostics\n\n3️⃣ Gujarat Matru Voucher\n💳 ₹4,000 voucher for nutrition\n🍎 Available at Anganwadi centers\n\n📞 Helpline: 104',
        'govt_schemes_menu': '🌿 Government Schemes\n\nSelect a scheme to learn more:',
        'scheme_pmmvy': '👶 PMMVY - Pradhan Mantri Matru Vandana Yojana\n\n💰 Benefit: ₹5,000 in 3 installments\n📋 Eligibility: First living child\n📝 Documents: Aadhar, Bank account, Pregnancy certificate\n📍 Apply at: Anganwadi Center or PHC\n📞 Helpline: 104\n\n✅ How to Apply:\n1. Visit nearest Anganwadi\n2. Fill Form 1A (during pregnancy)\n3. Fill Form 1B (after delivery)\n4. Money directly to bank account',
        'scheme_jssk': '🏥 JSSK - Janani Shishu Suraksha Karyakram\n\n💰 Benefit: 100% FREE delivery & care\n📋 Includes:\n• Free delivery (normal/C-section)\n• Free medicines & tests\n• Free ambulance (108)\n• Free food during stay\n• Free baby care for 30 days\n\n📍 Available at: All govt hospitals\n📞 Ambulance: 108\n📞 Helpline: 104\n\n✅ No registration needed - Just go to govt hospital!',
        'scheme_ma_amrutam': '💰 Maa Amrutam Yojana (Gujarat)\n\n💰 Benefit: FREE treatment up to ₹5 Lakh\n📋 Eligibility: BPL families in Gujarat\n🏥 Coverage:\n• All surgeries\n• Cancer treatment\n• Heart diseases\n• Kidney treatment\n• Maternity care\n\n📍 Apply at: Taluka Panchayat office\n📝 Documents: Ration card, Aadhar, Income certificate\n📞 Helpline: 1800-233-1022',
        'scheme_all_list': '📖 Complete Schemes List:\n\n👶 MOTHER & CHILD:\n1️⃣ PMMVY - ₹5,000 for 1st baby\n2️⃣ JSSK - Free delivery\n3️⃣ Gujarat Matru Voucher - ₹4,000\n4️⃣ Balsakha Yojana - Girl child support\n\n🏥 HEALTH INSURANCE:\n5️⃣ Maa Amrutam - ₹5L coverage\n6️⃣ Ayushman Bharat - ₹5L coverage\n7️⃣ PMJAY - Free treatment\n\n💊 MEDICINE & TREATMENT:\n8️⃣ Free Medicine Scheme - All govt hospitals\n9️⃣ 108 Ambulance - Free emergency\n🔟 104 Helpline - Free health advice\n\n🌾 NUTRITION:\n1️⃣1️⃣ Anganwadi Services - Free food\n1️⃣2️⃣ Mid-Day Meal - School children\n\n📞 Main Helpline: 104\n🚑 Emergency: 108\n📱 CM Helpline: 181',
        'growth_info': '👩‍🍼 Baby Growth by Week:\n\nWeek 12: Baby size of plum 🍑\nWeek 20: Baby size of banana 🍌\nWeek 28: Baby size of eggplant 🍆\nWeek 36: Baby size of papaya 🥭\n\n💡 Regular weight checks recommended!',
        'worker_menu': '👩‍⚕️ Health Worker Mode\n\nWhat would you like to do?',
        'worker_login_prompt': '🔐 Health Worker Login\n\nEnter your Worker ID:\n\nExample: ASHA001',
        'worker_login_success': '✅ Login Successful!\n\nWelcome, Health Worker {}',
        'worker_login_failed': '❌ Invalid Worker ID. Please try again.',
        'worker_patients': '📋 Your Patients:\n\n',
        'worker_emergencies': '🚨 Pending Emergencies:\n\n',
        'no_patients': '📭 No patients assigned.',
        'worker_register_name': '👩‍⚕️ Health Worker Registration\n\n👤 Enter your full name:',
        'worker_register_age': '🎂 Enter your age:',
        'worker_register_category': '🏷️ Select your category:',
        'worker_register_experience': '📅 Enter years of experience:',
        'worker_register_location': '📍 Share your location:',
        'worker_registration_sent': '✅ Registration sent!\n\nAdmin will review and approve soon.\n\nYou will be notified once approved.',
        'worker_not_approved': '⏳ Your registration is pending admin approval.\n\nPlease wait for confirmation.',
        'book_worker_menu': '💼 Book Health Worker\n\nNearby approved workers:',
        'no_workers_nearby': '📭 No health workers available nearby.',
        'raise_problem_menu': '📢 Raise Problem\n\nReport an issue or problem:',
        'issue_name_prompt': '👤 Enter your full name:',
        'issue_category_prompt': '🏷️ Select your category:',
        'issue_age_prompt': '🎂 Enter your age:',
        'issue_description_prompt': '📝 Describe your problem in detail:',
        'issue_submitted': '✅ Problem reported successfully!\n\nYour issue has been forwarded to admin.\n\nYou will be contacted soon.',
        'issue_error': '❌ Failed to submit problem. Please try again.',
        'xray_consent': '🩻 X-RAY REQUEST\n\n📝 Reply with:\nName|Age|Village|Symptoms\n\nExample: Ramesh Patel|45|Anklav|Cough 5 days chest pain\n\n⚠️ AI helps doctors only. Explicit consent required:',
        'xray_form_prompt': '📝 Enter patient details:\n\nFormat: Name|Age|Village|Symptoms\n\nExample: Ramesh Patel|45|Anklav|Cough 5 days chest pain',
        'xray_form_error': '❌ Wrong format!\n\nPlease use: Name|Age|Village|Symptoms',
        'xray_doctor_select': '✅ Form saved: {} ({}) {}\n\n👨‍⚕️ Choose PHC doctor:',
        'xray_sent': '✅ Sent to doctor!\n\nUse /status to check progress.\n\nDoctor will send PDF report here.',
        'xray_status': '📊 X-Ray Request Status:\n\n',
        'no_xray_requests': '📭 No X-ray requests found.',
    },
    'hi': {
        'welcome': '🏥 मेडीमाइंड रूरल में आपका स्वागत है!\n\nअपनी पसंदीदा भाषा चुनें:',
        'main_menu': '🏥 मेडीमाइंड रूरल - मुख्य मेनू\n\nएक सेवा चुनें:',
        'coming_soon': '⏳ सुविधा जल्द आ रही है!',
        'unknown': '❓ कृपया मेनू बटन या /start कमांड का उपयोग करें।',
        'hospital_prompt': '📍 अपना स्थान साझा करें या शहर के नाम से खोजें:',
        'searching': '🔍 आस-पास के अस्पतालों की खोज की जा रही है...',
        'no_hospitals': '❌ आस-पास कोई अस्पताल नहीं मिला।\n\n🔍 प्रयास करें: आनंद, वी.वी.नगर, अंकलाव',
        'error': '⚠️ त्रुटि हुई। कृपया पुनः प्रयास करें।',
        'disclaimer': '\n\n⚠️ अस्वीकरण: जाने से पहले विवरण सत्यापित करें।',
        'enter_city': '📝 शहर का नाम दर्ज करें (जैसे: आनंद, वी.वी.नगर, अंकलाव):',
        'hospitals_nearby': '🏥 आपके पास अस्पताल ({}):',
        'search_other': '\n\nअन्य शहर खोजें? आनंद/वी.वी.नगर',
        'emergency_prompt': '🚨 आपातकालीन सहायता\n\nतत्काल सहायता के लिए अपना लाइव स्थान साझा करें:',
        'sos_sent': '✅ SOS भेजा गया! मदद आ रही है!\n\n📍 आपका स्थान: {}',
        'sos_error': '❌ SOS भेजने में विफल। कृपया पुनः प्रयास करें या 108 पर कॉल करें।',
        'emergency_cancel': '❌ आपातकालीन अनुरोध रद्द किया गया।',
        'medicine_prompt': '💊 दवा अनुस्मारक सेटअप\n\nदवा का नाम दर्ज करें:',
        'medicine_time': '⏰ मुझे आपको कब याद दिलाना चाहिए?\n\nप्रारूप: 09:00 AM या 21:30',
        'medicine_dosage': '📋 खुराक/आवृत्ति?\n\nउदाहरण: दिन में 2 गोलियां, भोजन के बाद 1 चम्मच',
        'reminder_set': '✅ अनुस्मारक सेट किया गया!\n\n💊 {}\n⏰ {}\n📋 {}\n\nआपको रोज़ाना याद दिलाया जाएगा।',
        'reminder_error': '❌ अनुस्मारक सेट करने में विफल। कृपया पुनः प्रयास करें।',
        'list_reminders': '📋 आपके सक्रिय अनुस्मारक:',
        'no_reminders': '📭 कोई सक्रिय अनुस्मारक नहीं।',
        'reminder_stopped': '✅ अनुस्मारक सफलतापूर्वक हटाया गया।',
        'reminder_notification': '💊 दवा अनुस्मारक!\n\n{}\n📋 {}\n\n⏰ अपनी दवा लेने का समय!',
        'medicine_menu': '💊 दवा अनुस्मारक\n\nआप क्या करना चाहेंगे?',
        'delete_prompt': '🗑️ अनुस्मारक हटाएं\n\nहटाने के लिए अनुस्मारक संख्या दर्ज करें:',
        'visit_menu': '📅 यात्रा योजनाकार\n\nआप क्या करना चाहेंगे?',
        'appointment_hospital': '🏥 डॉक्टर/अस्पताल का नाम दर्ज करें:',
        'appointment_date': '📅 तारीख दर्ज करें (DD-MM-YYYY):\n\nउदाहरण: 23-02-2026',
        'appointment_time': '⏰ समय दर्ज करें (HH:MM AM/PM):\n\nउदाहरण: 10:00 AM',
        'appointment_notes': '📝 नोट्स दर्ज करें (वैकल्पिक):\n\nउदाहरण: BP चेक फॉलो-अप',
        'appointment_booked': '✅ अपॉइंटमेंट बुक हो गया!\n\n🏥 {}\n📅 {}\n⏰ {}\n📝 {}\n\n🔔 आपको 1 दिन पहले याद दिलाया जाएगा।',
        'appointment_error': '❌ अपॉइंटमेंट बुक करने में विफल। कृपया पुनः प्रयास करें।',
        'list_appointments': '📋 आपके आगामी अपॉइंटमेंट:',
        'no_appointments': '📭 कोई आगामी अपॉइंटमेंट नहीं।',
        'appointment_reminder': '🔔 अपॉइंटमेंट अनुस्मारक!\n\nकल {} बजे\n🏥 {}\n📝 {}\n\nमत भूलना!',
        'cancel_appointment_prompt': '❌ अपॉइंटमेंट रद्द करें\n\nरद्द करने के लिए अपॉइंटमेंट संख्या दर्ज करें:',
        'appointment_cancelled': '✅ अपॉइंटमेंट सफलतापूर्वक रद्द किया गया।',
        'maternal_menu': '👶 मातृ स्वास्थ्य\n\nआप क्या जानना चाहेंगे?',
        'lmp_prompt': '🤰 गर्भावस्था सप्ताह कैलकुलेटर\n\nअपनी अंतिम माहवारी (LMP) तारीख दर्ज करें:\n\nप्रारूप: DD-MM-YYYY\nउदाहरण: 01-01-2026',
        'pregnancy_result': '🤰 गर्भावस्था जानकारी:\n\n📅 LMP: {}\n⏰ गर्भावस्था सप्ताह: {} सप्ताह\n👶 प्रसव तिथि: {}\n🏥 अगली ANC जांच: {}\n\n💡 सुझाव: नियमित जांच महत्वपूर्ण है!',
        'maternal_error': '❌ गलत तारीख प्रारूप। कृपया DD-MM-YYYY उपयोग करें',
        'schemes_info': '🌿 गुजरात माँ और बच्चे की योजनाएं:\n\n1️⃣ PMMVY (प्रधानमंत्री मातृ वंदना योजना)\n💰 ₹5,000 तीन किस्तों में\n📋 पहले जीवित बच्चे के लिए\n\n2️⃣ JSSK (जननी शिशु सुरक्षा कार्यक्रम)\n🏥 सरकारी अस्पतालों में मुफ्त प्रसव\n💊 मुफ्त दवाएं और जांच\n\n3️⃣ गुजरात मातृ वाउचर\n💳 पोषण के लिए ₹4,000 वाउचर\n🍎 आंगनवाड़ी केंद्रों पर उपलब्ध\n\n📞 हेल्पलाइन: 104',
        'govt_schemes_menu': '🌿 सरकारी योजनाएं\n\nअधिक जानने के लिए योजना चुनें:',
        'scheme_pmmvy': '👶 PMMVY - प्रधानमंत्री मातृ वंदना योजना\n\n💰 लाभ: ₹5,000 तीन किस्तों में\n📋 पात्रता: पहला जीवित बच्चा\n📝 दस्तावेज: आधार, बैंक खाता, गर्भावस्था प्रमाण पत्र\n📍 आवेदन करें: आंगनवाड़ी केंद्र या PHC\n📞 हेल्पलाइन: 104\n\n✅ आवेदन कैसे करें:\n1. निकटतम आंगनवाड़ी पर जाएं\n2. फॉर्म 1A भरें (गर्भावस्था के दौरान)\n3. फॉर्म 1B भरें (प्रसव के बाद)\n4. पैसा सीधे बैंक खाते में',
        'scheme_jssk': '🏥 JSSK - जननी शिशु सुरक्षा कार्यक्रम\n\n💰 लाभ: 100% मुफ्त प्रसव और देखभाल\n📋 शामिल:\n• मुफ्त प्रसव (सामान्य/सी-सेक्शन)\n• मुफ्त दवाएं और जांच\n• मुफ्त एम्बुलेंस (108)\n• रहने के दौरान मुफ्त भोजन\n• 30 दिनों के लिए मुफ्त बच्चे की देखभाल\n\n📍 उपलब्ध: सभी सरकारी अस्पतालों में\n📞 एम्बुलेंस: 108\n📞 हेल्पलाइन: 104\n\n✅ कोई पंजीकरण की आवश्यकता नहीं - बस सरकारी अस्पताल जाएं!',
        'scheme_ma_amrutam': '💰 माँ अमृतम योजना (गुजरात)\n\n💰 लाभ: ₹5 लाख तक मुफ्त इलाज\n📋 पात्रता: गुजरात में BPL परिवार\n🏥 कवरेज:\n• सभी सर्जरी\n• कैंसर का इलाज\n• हृदय रोग\n• किडनी का इलाज\n• मातृत्व देखभाल\n\n📍 आवेदन करें: तालुका पंचायत कार्यालय\n📝 दस्तावेज: राशन कार्ड, आधार, आय प्रमाण पत्र\n📞 हेल्पलाइन: 1800-233-1022',
        'scheme_all_list': '📖 पूर्ण योजना सूची:\n\n👶 माँ और बच्चा:\n1️⃣ PMMVY - पहले बच्चे के लिए ₹5,000\n2️⃣ JSSK - मुफ्त प्रसव\n3️⃣ गुजरात मातृ वाउचर - ₹4,000\n4️⃣ बालसखा योजना - बालिका सहायता\n\n🏥 स्वास्थ्य बीमा:\n5️⃣ माँ अमृतम - ₹5L कवरेज\n6️⃣ आयुष्मान भारत - ₹5L कवरेज\n7️⃣ PMJAY - मुफ्त इलाज\n\n💊 दवा और इलाज:\n8️⃣ मुफ्त दवा योजना - सभी सरकारी अस्पताल\n9️⃣ 108 एम्बुलेंस - मुफ्त आपातकाल\n🔟 104 हेल्पलाइन - मुफ्त स्वास्थ्य सलाह\n\n🌾 पोषण:\n1️⃣1️⃣ आंगनवाड़ी सेवाएं - मुफ्त भोजन\n1️⃣2️⃣ मिड-डे मील - स्कूली बच्चे\n\n📞 मुख्य हेल्पलाइन: 104\n🚑 आपातकाल: 108\n📱 CM हेल्पलाइन: 181',
        'growth_info': '👩‍🍼 सप्ताह के अनुसार बच्चे की वृद्धि:\n\nसप्ताह 12: बेर के आकार का 🍑\nसप्ताह 20: केले के आकार का 🍌\nसप्ताह 28: बैंगन के आकार का 🍆\nसप्ताह 36: पपीते के आकार का 🥭\n\n💡 नियमित वजन जांच अनुशंसित!',
        'worker_menu': '👩‍⚕️ स्वास्थ्य कार्यकर्ता मोड\n\nआप क्या करना चाहेंगे?',
        'worker_login_prompt': '🔐 स्वास्थ्य कार्यकर्ता लॉगिन\n\nअपनी कार्यकर्ता ID दर्ज करें:\n\nउदाहरण: ASHA001',
        'worker_login_success': '✅ लॉगिन सफल!\n\nस्वागत है, स्वास्थ्य कार्यकर्ता {}',
        'worker_login_failed': '❌ अमान्य कार्यकर्ता ID। कृपया पुनः प्रयास करें।',
        'worker_patients': '📋 आपके मरीज:\n\n',
        'worker_emergencies': '🚨 लंबित आपातकाल:\n\n',
        'no_patients': '📭 कोई मरीज नहीं सौंपा गया।',
        'worker_register_name': '👩‍⚕️ स्वास्थ्य कार्यकर्ता पंजीकरण\n\n👤 अपना पूरा नाम दर्ज करें:',
        'worker_register_age': '🎂 अपनी उम्र दर्ज करें:',
        'worker_register_category': '🏷️ अपनी श्रेणी चुनें:',
        'worker_register_experience': '📅 अनुभव के वर्ष दर्ज करें:',
        'worker_register_location': '📍 अपना स्थान साझा करें:',
        'worker_registration_sent': '✅ पंजीकरण भेजा गया!\n\nएडमिन जल्द ही समीक्षा और अनुमोदन करेगा।\n\nअनुमोदित होने पर आपको सूचित किया जाएगा।',
        'worker_not_approved': '⏳ आपका पंजीकरण एडमिन अनुमोदन लंबित है।\n\nकृपया पुष्टि की प्रतीक्षा करें।',
        'book_worker_menu': '💼 स्वास्थ्य कार्यकर्ता बुक करें\n\nआस-पास के अनुमोदित कार्यकर्ता:',
        'no_workers_nearby': '📭 आस-पास कोई स्वास्थ्य कार्यकर्ता उपलब्ध नहीं।',
        'raise_problem_menu': '📢 समस्या दर्ज करें\n\nकोई समस्या या मुद्दा रिपोर्ट करें:',
        'issue_name_prompt': '👤 अपना पूरा नाम दर्ज करें:',
        'issue_category_prompt': '🏷️ अपनी श्रेणी चुनें:',
        'issue_age_prompt': '🎂 अपनी उम्र दर्ज करें:',
        'issue_description_prompt': '📝 अपनी समस्या का विस्तार से वर्णन करें:',
        'issue_submitted': '✅ समस्या सफलतापूर्वक रिपोर्ट की गई!\n\nआपकी समस्या एडमिन को भेज दी गई है।\n\nआपसे जल्द ही संपर्क किया जाएगा।',
        'issue_error': '❌ समस्या सबमिट करने में विफल। कृपया पुनः प्रयास करें।',
        'xray_consent': '🩻 एक्स-रे अनुरोध\n\n📝 उत्तर दें:\nनाम|उम्र|गांव|लक्षण\n\nउदाहरण: रमेश पटेल|45|अंकलाव|5 दिन से खांसी सीने में दर्द\n\n⚠️ AI केवल डॉक्टरों की मदद करता है। स्पष्ट सहमति आवश्यक:',
        'xray_form_prompt': '📝 रोगी विवरण दर्ज करें:\n\nप्रारूप: नाम|उम्र|गांव|लक्षण\n\nउदाहरण: रमेश पटेल|45|अंकलाव|5 दिन से खांसी सीने में दर्द',
        'xray_form_error': '❌ गलत प्रारूप!\n\nकृपया उपयोग करें: नाम|उम्र|गांव|लक्षण',
        'xray_doctor_select': '✅ फॉर्म सहेजा गया: {} ({}) {}\n\n👨‍⚕️ PHC डॉक्टर चुनें:',
        'xray_sent': '✅ डॉक्टर को भेजा गया!\n\nप्रगति जांचने के लिए /status उपयोग करें।\n\nडॉक्टर यहां PDF रिपोर्ट भेजेंगे।',
        'xray_status': '📊 एक्स-रे अनुरोध स्थिति:\n\n',
        'no_xray_requests': '📭 कोई एक्स-रे अनुरोध नहीं मिला।',
    },
    'gu': {
        'welcome': '🏥 મેડીમાઇન્ડ રૂરલમાં આપનું સ્વાગત છે!\n\nતમારી પસંદીદી ભાષા પસંદ કરો:',
        'main_menu': '🏥 મેડીમાઇન્ડ રૂરલ - મુખ્ય મેનૂ\n\nસેવા પસંદ કરો:',
        'coming_soon': '⏳ સુવિધા ટૂંક સમયમાં આવી રહી છે!',
        'unknown': '❓ કૃપા કરીને મેનૂ બટન અથવા /start આદેશનો ઉપયોગ કરો.',
        'hospital_prompt': '📍 તમારું સ્થાન શેર કરો અથવા શહેરના નામથી શોધો:',
        'searching': '🔍 નજીકની હોસ્પિટલો શોધી રહ્યા છીએ...',
        'no_hospitals': '❌ નજીકમાં કોઈ હોસ્પિટલ મળી નથી।\n\n🔍 પ્રયાસ કરો: આણંદ, વી.વી.નગર, અંકલાવ',
        'error': '⚠️ ભૂલ થઈ. કૃપા કરીને ફરી પ્રયાસ કરો.',
        'disclaimer': '\n\n⚠️ ચેતવણી: મુલાકાત લેતા પહેલા વિગતો ચકાસો.',
        'enter_city': '📝 શહેરનું નામ દાખલ કરો (દા.ત.: આણંદ, વી.વી.નગર, અંકલાવ):',
        'hospitals_nearby': '🏥 તમારી નજીકની હોસ્પિટલો ({}):',
        'search_other': '\n\nબીજું શહેર શોધો? આણંદ/વી.વી.નગર',
        'emergency_prompt': '🚨 કટોકટી સહાય\n\nતાત્કાલિક સહાય માટે તમારું લાઇવ સ્થાન શેર કરો:',
        'sos_sent': '✅ SOS મોકલ્યું! મદદ આવી રહી છે!\n\n📍 તમારું સ્થાન: {}',
        'sos_error': '❌ SOS મોકલવામાં નિષ્ફળ. કૃપા કરીને ફરી પ્રયાસ કરો અથવા 108 પર કૉલ કરો.',
        'emergency_cancel': '❌ કટોકટી વિનંતી રદ કરી.',
        'medicine_prompt': '💊 દવા રીમાઇન્ડર સેટઅપ\n\nદવાનું નામ દાખલ કરો:',
        'medicine_time': '⏰ મારે તમને ક્યારે યાદ અપાવવું જોઈએ?\n\nફોર્મેટ: 09:00 AM અથવા 21:30',
        'medicine_dosage': '📋 ડોઝ/આવર્તન?\n\nઉદાહરણ: દરરોજ 2 ગોળીઓ, ભોજન પછી 1 ચમચી',
        'reminder_set': '✅ રીમાઇન્ડર સેટ થયું!\n\n💊 {}\n⏰ {}\n📋 {}\n\nતમને દરરોજ યાદ અપાવવામાં આવશે.',
        'reminder_error': '❌ રીમાઇન્ડર સેટ કરવામાં નિષ્ફળ. કૃપા કરીને ફરી પ્રયાસ કરો.',
        'list_reminders': '📋 તમારા સક્રિય રીમાઇન્ડર્સ:',
        'no_reminders': '📭 કોઈ સક્રિય રીમાઇન્ડર નથી.',
        'reminder_stopped': '✅ રીમાઇન્ડર સફળતાપૂર્વક કાઢી નાખ્યું.',
        'reminder_notification': '💊 દવા રીમાઇન્ડર!\n\n{}\n📋 {}\n\n⏰ તમારી દવા લેવાનો સમય!',
        'medicine_menu': '💊 દવા રીમાઇન્ડર\n\nતમે શું કરવા માંગો છો?',
        'delete_prompt': '🗑️ રીમાઇન્ડર કાઢી નાખો\n\nકાઢી નાખવા માટે રીમાઇન્ડર નંબર દાખલ કરો:',
        'visit_menu': '📅 મુલાકાત આયોજક\n\nતમે શું કરવા માંગો છો?',
        'appointment_hospital': '🏥 ડૉક્ટર/હોસ્પિટલનું નામ દાખલ કરો:',
        'appointment_date': '📅 તારીખ દાખલ કરો (DD-MM-YYYY):\n\nઉદાહરણ: 23-02-2026',
        'appointment_time': '⏰ સમય દાખલ કરો (HH:MM AM/PM):\n\nઉદાહરણ: 10:00 AM',
        'appointment_notes': '📝 નોંધ દાખલ કરો (વૈકલ્પિક):\n\nઉદાહરણ: BP ચેક ફોલો-અપ',
        'appointment_booked': '✅ એપોઇન્ટમેન્ટ બુક થઈ!\n\n🏥 {}\n📅 {}\n⏰ {}\n📝 {}\n\n🔔 તમને 1 દિવસ પહેલા યાદ અપાવવામાં આવશે.',
        'appointment_error': '❌ એપોઇન્ટમેન્ટ બુક કરવામાં નિષ્ફળ. કૃપા કરીને ફરી પ્રયાસ કરો.',
        'list_appointments': '📋 તમારી આગામી એપોઇન્ટમેન્ટ્સ:',
        'no_appointments': '📭 કોઈ આગામી એપોઇન્ટમેન્ટ નથી.',
        'appointment_reminder': '🔔 એપોઇન્ટમેન્ટ રીમાઇન્ડર!\n\nઆવતીકાલે {} વાગ્યે\n🏥 {}\n📝 {}\n\nભૂલશો નહીં!',
        'cancel_appointment_prompt': '❌ એપોઇન્ટમેન્ટ રદ કરો\n\nરદ કરવા માટે એપોઇન્ટમેન્ટ નંબર દાખલ કરો:',
        'appointment_cancelled': '✅ એપોઇન્ટમેન્ટ સફળતાપૂર્વક રદ થઈ.',
        'maternal_menu': '👶 માતૃત્વ આરોગ્ય\n\nતમે શું જાણવા માંગો છો?',
        'lmp_prompt': '🤰 ગર્ભાવસ્થા અઠવાડિયું કેલ્ક્યુલેટર\n\nતમારી છેલ્લી માસિક (LMP) તારીખ દાખલ કરો:\n\nફોર્મેટ: DD-MM-YYYY\nઉદાહરણ: 01-01-2026',
        'pregnancy_result': '🤰 ગર્ભાવસ્થા માહિતી:\n\n📅 LMP: {}\n⏰ ગર્ભાવસ્થા અઠવાડિયા: {} અઠવાડિયા\n👶 પ્રસૂતિ તારીખ: {}\n🏥 આગલી ANC મુલાકાત: {}\n\n💡 ટિપ: નિયમિત તપાસ મહત્વપૂર્ણ છે!',
        'maternal_error': '❌ અમાન્ય તારીખ ફોર્મેટ. કૃપા કરીને DD-MM-YYYY વાપરો',
        'schemes_info': '🌿 ગુજરાત માતા અને બાળક યોજનાઓ:\n\n1️⃣ PMMVY (પ્રધાનમંત્રી માતૃ વંદના યોજના)\n💰 ₹5,000 ત્રણ હપ્તામાં\n📋 પ્રથમ જીવંત બાળક માટે\n\n2️⃣ JSSK (જનની શિશુ સુરક્ષા કાર્યક્રમ)\n🏥 સરકારી હોસ્પિટલોમાં મફત પ્રસૂતિ\n💊 મફત દવાઓ અને નિદાન\n\n3️⃣ ગુજરાત માતૃ વાઉચર\n💳 પોષણ માટે ₹4,000 વાઉચર\n🍎 આંગણવાડી કેન્દ્રો પર ઉપલબ્ધ\n\n📞 હેલ્પલાઇન: 104',
        'govt_schemes_menu': '🌿 સરકારી યોજનાઓ\n\nવધુ જાણવા માટે યોજના પસંદ કરો:',
        'scheme_pmmvy': '👶 PMMVY - પ્રધાનમંત્રી માતૃ વંદના યોજના\n\n💰 લાભ: ₹5,000 ત્રણ હપ્તામાં\n📋 પાત્રતા: પ્રથમ જીવંત બાળક\n📝 દસ્તાવેજો: આધાર, બેંક ખાતું, ગર્ભાવસ્થા પ્રમાણપત્ર\n📍 અરજી કરો: આંગણવાડી કેન્દ્ર અથવા PHC\n📞 હેલ્પલાઇન: 104\n\n✅ અરજી કેવી રીતે કરવી:\n1. નજીકની આંગણવાડી પર જાઓ\n2. ફોર્મ 1A ભરો (ગર્ભાવસ્થા દરમિયાન)\n3. ફોર્મ 1B ભરો (પ્રસૂતિ પછી)\n4. પૈસા સીધા બેંક ખાતામાં',
        'scheme_jssk': '🏥 JSSK - જનની શિશુ સુરક્ષા કાર્યક્રમ\n\n💰 લાભ: 100% મફત પ્રસૂતિ અને સંભાળ\n📋 સમાવેશ:\n• મફત પ્રસૂતિ (સામાન્ય/સી-સેક્શન)\n• મફત દવાઓ અને પરીક્ષણો\n• મફત એમ્બ્યુલન્સ (108)\n• રહેવા દરમિયાન મફત ભોજન\n• 30 દિવસ માટે મફત બાળક સંભાળ\n\n📍 ઉપલબ્ધ: બધી સરકારી હોસ્પિટલોમાં\n📞 એમ્બ્યુલન્સ: 108\n📞 હેલ્પલાઇન: 104\n\n✅ કોઈ નોંધણીની જરૂર નથી - ફક્ત સરકારી હોસ્પિટલમાં જાઓ!',
        'scheme_ma_amrutam': '💰 માં અમૃતમ યોજના (ગુજરાત)\n\n💰 લાભ: ₹5 લાખ સુધી મફત સારવાર\n📋 પાત્રતા: ગુજરાતમાં BPL પરિવારો\n🏥 કવરેજ:\n• બધી સર્જરી\n• કેન્સર સારવાર\n• હૃદય રોગ\n• કિડની સારવાર\n• માતૃત્વ સંભાળ\n\n📍 અરજી કરો: તાલુકા પંચાયત કચેરી\n📝 દસ્તાવેજો: રેશન કાર્ડ, આધાર, આવક પ્રમાણપત્ર\n📞 હેલ્પલાઇન: 1800-233-1022',
        'scheme_all_list': '📖 સંપૂર્ણ યોજના યાદી:\n\n👶 માતા અને બાળક:\n1️⃣ PMMVY - પ્રથમ બાળક માટે ₹5,000\n2️⃣ JSSK - મફત પ્રસૂતિ\n3️⃣ ગુજરાત માતૃ વાઉચર - ₹4,000\n4️⃣ બાલસખા યોજના - બાળિકા સહાય\n\n🏥 આરોગ્ય વીમો:\n5️⃣ માં અમૃતમ - ₹5L કવરેજ\n6️⃣ આયુષ્માન ભારત - ₹5L કવરેજ\n7️⃣ PMJAY - મફત સારવાર\n\n💊 દવા અને સારવાર:\n8️⃣ મફત દવા યોજના - બધી સરકારી હોસ્પિટલો\n9️⃣ 108 એમ્બ્યુલન્સ - મફત કટોકટી\n🔟 104 હેલ્પલાઇન - મફત આરોગ્ય સલાહ\n\n🌾 પોષણ:\n1️⃣1️⃣ આંગણવાડી સેવાઓ - મફત ભોજન\n1️⃣2️⃣ મિડ-ડે મીલ - શાળાના બાળકો\n\n📞 મુખ્ય હેલ્પલાઇન: 104\n🚑 કટોકટી: 108\n📱 CM હેલ્પલાઇન: 181',
        'growth_info': '👩‍🍼 અઠવાડિયા પ્રમાણે બાળકની વૃદ્ધિ:\n\nઅઠવાડિયું 12: બેરના કદનું 🍑\nઅઠવાડિયું 20: કેળાના કદનું 🍌\nઅઠવાડિયું 28: રીંગણના કદનું 🍆\nઅઠવાડિયું 36: પપૈયાના કદનું 🥭\n\n💡 નિયમિત વજન તપાસ ભલામણ કરેલ!',
        'worker_menu': '👩‍⚕️ આરોગ્ય કાર્યકર મોડ\n\nતમે શું કરવા માંગો છો?',
        'worker_login_prompt': '🔐 આરોગ્ય કાર્યકર લૉગિન\n\nતમારી કાર્યકર ID દાખલ કરો:\n\nઉદાહરણ: ASHA001',
        'worker_login_success': '✅ લૉગિન સફળ!\n\nસ્વાગત છે, આરોગ્ય કાર્યકર {}',
        'worker_login_failed': '❌ અમાન્ય કાર્યકર ID. કૃપા કરીને ફરી પ્રયાસ કરો.',
        'worker_patients': '📋 તમારા દર્દીઓ:\n\n',
        'worker_emergencies': '🚨 બાકી કટોકટી:\n\n',
        'no_patients': '📭 કોઈ દર્દી સોંપાયેલ નથી.',
        'worker_register_name': '👩‍⚕️ આરોગ્ય કાર્યકર નોંધણી\n\n👤 તમારું પૂરું નામ દાખલ કરો:',
        'worker_register_age': '🎂 તમારી ઉંમર દાખલ કરો:',
        'worker_register_category': '🏷️ તમારી શ્રેણી પસંદ કરો:',
        'worker_register_experience': '📅 અનુભવના વર્ષો દાખલ કરો:',
        'worker_register_location': '📍 તમારું સ્થાન શેર કરો:',
        'worker_registration_sent': '✅ નોંધણી મોકલી!\n\nએડમિન ટૂંક સમયમાં સમીક્ષા અને મંજૂરી આપશે.\n\nમંજૂર થયા પછી તમને સૂચિત કરવામાં આવશે.',
        'worker_not_approved': '⏳ તમારી નોંધણી એડમિન મંજૂરી બાકી છે.\n\nકૃપા કરીને પુષ્ટિની રાહ જુઓ.',
        'book_worker_menu': '💼 આરોગ્ય કાર્યકર બુક કરો\n\nનજીકના મંજૂર કાર્યકરો:',
        'no_workers_nearby': '📭 નજીકમાં કોઈ આરોગ્ય કાર્યકર ઉપલબ્ધ નથી.',
        'raise_problem_menu': '📢 સમસ્યા નોંધાવો\n\nકોઈ સમસ્યા અથવા મુદ્દો રિપોર્ટ કરો:',
        'issue_name_prompt': '👤 તમારું પૂરું નામ દાખલ કરો:',
        'issue_category_prompt': '🏷️ તમારી શ્રેણી પસંદ કરો:',
        'issue_age_prompt': '🎂 તમારી ઉંમર દાખલ કરો:',
        'issue_description_prompt': '📝 તમારી સમસ્યાનું વિગતવાર વર્ણન કરો:',
        'issue_submitted': '✅ સમસ્યા સફળતાપૂર્વક રિપોર્ટ થઈ!\n\nતમારી સમસ્યા એડમિનને મોકલી દેવામાં આવી છે।\n\nતમારો ટૂંક સમયમાં સંપર્ક કરવામાં આવશે।',
        'issue_error': '❌ સમસ્યા સબમિટ કરવામાં નિષ્ફળ. કૃપા કરીને ફરી પ્રયાસ કરો.',
        'medicine_prompt': '💊 દવા રીમાઇન્ડર સેટઅપ\n\nદવાનું નામ દાખલ કરો:',
        'medicine_time': '⏰ મારે તમને ક્યારે યાદ અપાવવું જોઈએ?\n\nફોર્મેટ: 09:00 AM અથવા 21:30',
        'medicine_dosage': '📋 ડોઝ/આવર્તન?\n\nઉદાહરણ: દરરોજ 2 ગોળીઓ, ભોજન પછી 1 ચમચી',
        'reminder_set': '✅ રીમાઇન્ડર સેટ થયું!\n\n💊 {}\n⏰ {}\n📋 {}\n\nતમને દરરોજ યાદ અપાવવામાં આવશે.',
        'reminder_error': '❌ રીમાઇન્ડર સેટ કરવામાં નિષ્ફળ. કૃપા કરીને ફરી પ્રયાસ કરો.',
        'list_reminders': '💊 તમારા સક્રિય રીમાઇન્ડર્સ:',
        'no_reminders': '📭 કોઈ સક્રિય રીમાઇન્ડર નથી.',
        'reminder_stopped': '✅ રીમાઇન્ડર બંધ થયું.',
        'reminder_notification': '💊 દવા રીમાઇન્ડર!\n\n{}\n📋 {}\n\n⏰ તમારી દવા લેવાનો સમય!',
        'xray_consent': '🩻 એક્સ-રે અનુરોધ\n\n📝 જવાબ આપો:\nનામ|ઉંમર|ગામ|લક્ષણો\n\nઉદાહરણ: રમેશ પટેલ|45|અંકલાવ|5 દિવસથી ઉધરસ છાતીમાં દુખાવો\n\n⚠️ AI ફક્ત ડૉક્ટરોને મદદ કરે છે. સ્પષ્ટ સંમતિ જરૂરી:',
        'xray_form_prompt': '📝 દર્દીની વિગતો દાખલ કરો:\n\nફોર્મેટ: નામ|ઉંમર|ગામ|લક્ષણો\n\nઉદાહરણ: રમેશ પટેલ|45|અંકલાવ|5 દિવસથી ઉધરસ છાતીમાં દુખાવો',
        'xray_form_error': '❌ ખોટું ફોર્મેટ!\n\nકૃપા કરીને વાપરો: નામ|ઉંમર|ગામ|લક્ષણો',
        'xray_doctor_select': '✅ ફોર્મ સાચવ્યું: {} ({}) {}\n\n👨‍⚕️ PHC ડૉક્ટર પસંદ કરો:',
        'xray_sent': '✅ ડૉક્ટરને મોકલ્યું!\n\nપ્રગતિ તપાસવા /status વાપરો।\n\nડૉક્ટર અહીં PDF રિપોર્ટ મોકલશે।',
        'xray_status': '📊 એક્સ-રે અનુરોધ સ્થિતિ:\n\n',
        'no_xray_requests': '📭 કોઈ એક્સ-રે અનુરોધ મળ્યો નહીં।',
    }
}

MENU_BUTTONS = {
    'en': [
        ['🏥 Nearest Hospital', '🚑 Emergency Help'],
        ['💊 Medicine Reminder', '📅 Visit Planner'],
        ['👶 Maternal Health', '🩻 X-Ray Check'],
        ['👩‍⚕️ Health Worker Mode', '🌿 Govt Schemes'],
        ['📢 Raise Problem', '🔄 Change Language']
    ],
    'hi': [
        ['🏥 निकटतम अस्पताल', '🚑 आपातकालीन सहायता'],
        ['💊 दवा अनुस्मारक', '📅 यात्रा योजनाकार'],
        ['👶 मातृ स्वास्थ्य', '🩻 एक्स-रे जांच'],
        ['👩‍⚕️ स्वास्थ्य कार्यकर्ता मोड', '🌿 सरकारी योजनाएं'],
        ['📢 समस्या दर्ज करें', '🔄 भाषा बदलें']
    ],
    'gu': [
        ['🏥 નજીકની હોસ્પિટલ', '🚑 કટોકટી સહાય'],
        ['💊 દવા રીમાઇન્ડર', '📅 મુલાકાત આયોજક'],
        ['👶 માતૃત્વ આરોગ્ય', '🩻 એક્સ-રે તપાસ'],
        ['👩‍⚕️ આરોગ્ય કાર્યકર મોડ', '🌿 સરકારી યોજનાઓ'],
        ['📢 સમસ્યા નોંધાવો', '🔄 ભાષા બદલો']
    ]
}

NUMBER_EMOJIS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

CITY_BBOX = {
    'anklav': (22.1, 72.5, 22.4, 72.9),
    'anand': (22.50, 72.85, 22.60, 73.05),
    'v.v.nagar': (22.52, 72.90, 22.58, 73.00),
    'vvnagar': (22.52, 72.90, 22.58, 73.00),
    'vadodara': (22.25, 73.10, 22.35, 73.25),
    'ahmedabad': (22.95, 72.50, 23.15, 72.70),
}

def get_bbox_for_location(lat, lon, radius_km=10):
    """Calculate bounding box for location"""
    lat_offset = radius_km / 111.0
    lon_offset = radius_km / (111.0 * 111.0)
    
    return (lat - lat_offset, lon - lon_offset, lat + lat_offset, lon + lon_offset)

def get_language_keyboard():
    keyboard = [
        [InlineKeyboardButton("English 🇺🇸", callback_data='lang_en')],
        [InlineKeyboardButton("हिंदी 🇮🇳", callback_data='lang_hi')],
        [InlineKeyboardButton("ગુજરાતી 🇮🇳", callback_data='lang_gu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard(language: str):
    buttons = MENU_BUTTONS.get(language, MENU_BUTTONS['en'])
    menu_ids = [
        ['hospital', 'emergency'],
        ['medicine', 'visit'],
        ['maternal', 'xray_check'],
        ['worker', 'schemes'],
        ['raise_problem', 'change_lang']
    ]
    keyboard = []
    for row_btns, row_ids in zip(buttons, menu_ids):
        if len(row_btns) == 1:
            keyboard.append([InlineKeyboardButton(row_btns[0], callback_data=f'menu_{row_ids[0]}')])
        else:
            keyboard.append([InlineKeyboardButton(btn, callback_data=f'menu_{id}') for btn, id in zip(row_btns, row_ids)])
    return InlineKeyboardMarkup(keyboard)

def get_change_language_keyboard(language: str):
    back_text = '🔙 Back to Menu' if language == 'en' else '🔙 मेनू पर वापस जाएं' if language == 'hi' else '🔙 મેનૂ પર પાછા'
    change_text = '🔄 Change Language' if language == 'en' else '🔄 भाषा बदलें' if language == 'hi' else '🔄 ભાષા બદલો'
    keyboard = [
        [InlineKeyboardButton(back_text, callback_data='back_menu')],
        [InlineKeyboardButton(change_text, callback_data='change_lang')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_hospital_search_keyboard(language: str):
    share_text = '📍 Share Location' if language == 'en' else '📍 स्थान साझा करें' if language == 'hi' else '📍 સ્થાન શેર કરો'
    city_text = '🔍 Search by City Name' if language == 'en' else '🔍 शहर के नाम से खोजें' if language == 'hi' else '🔍 શહેરના નામથી શોધો'
    keyboard = [
        [KeyboardButton(share_text, request_location=True)],
        [KeyboardButton(city_text)]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

def get_hospital_results_keyboard(language: str):
    city_text = '🔍 Another City' if language == 'en' else '🔍 अन्य शहर' if language == 'hi' else '🔍 બીજું શહેર'
    location_text = '📍 My Location Again' if language == 'en' else '📍 मेरा स्थान फिर से' if language == 'hi' else '📍 મારું સ્થાન ફરીથી'
    menu_text = '🏠 Main Menu' if language == 'en' else '🏠 मुख्य मेनू' if language == 'hi' else '🏠 મુખ્ય મેનૂ'
    keyboard = [
        [InlineKeyboardButton(city_text, callback_data='search_city')],
        [InlineKeyboardButton(location_text, callback_data='menu_hospital')],
        [InlineKeyboardButton(menu_text, callback_data='back_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_emergency_keyboard(language: str):
    share_text = '📍 Share Location' if language == 'en' else '📍 स्थान साझा करें' if language == 'hi' else '📍 સ્થાન શેર કરો'
    cancel_text = '❌ Cancel' if language == 'en' else '❌ रद्द करें' if language == 'hi' else '❌ રદ કરો'
    keyboard = [
        [KeyboardButton(share_text, request_location=True)],
        [KeyboardButton(cancel_text)]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

def get_medicine_keyboard(language: str):
    list_text = '📋 My Reminders' if language == 'en' else '📋 मेरे अनुस्मारक' if language == 'hi' else '📋 મારા રીમાઇન્ડર્સ'
    new_text = '➕ Set New Reminder' if language == 'en' else '➕ नया अनुस्मारक सेट करें' if language == 'hi' else '➕ નવું રીમાઇન્ડર સેટ કરો'
    delete_text = '🗑️ Delete Reminder' if language == 'en' else '🗑️ अनुस्मारक हटाएं' if language == 'hi' else '🗑️ રીમાઇન્ડર કાઢી નાખો'
    menu_text = '🏠 Back to Main Menu' if language == 'en' else '🏠 मुख्य मेनू पर वापस' if language == 'hi' else '🏠 મુખ્ય મેનૂ પર પાછા'
    keyboard = [
        [InlineKeyboardButton(list_text, callback_data='list_reminders')],
        [InlineKeyboardButton(new_text, callback_data='new_reminder')],
        [InlineKeyboardButton(delete_text, callback_data='delete_reminder')],
        [InlineKeyboardButton(menu_text, callback_data='back_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_visit_keyboard(language: str):
    list_text = '📋 My Appointments' if language == 'en' else '📋 मेरे अपॉइंटमेंट' if language == 'hi' else '📋 મારી એપોઇન્ટમેન્ટ્સ'
    new_text = '➕ Book New Visit' if language == 'en' else '➕ नया अपॉइंटमेंट बुक करें' if language == 'hi' else '➕ નવી મુલાકાત બુક કરો'
    cancel_text = '❌ Cancel Appointment' if language == 'en' else '❌ अपॉइंटमेंट रद्द करें' if language == 'hi' else '❌ એપોઇન્ટમેન્ટ રદ કરો'
    menu_text = '🏠 Back to Main Menu' if language == 'en' else '🏠 मुख्य मेनू पर वापस' if language == 'hi' else '🏠 મુખ્ય મેનૂ પર પાછા'
    keyboard = [
        [InlineKeyboardButton(list_text, callback_data='list_appointments')],
        [InlineKeyboardButton(new_text, callback_data='new_appointment')],
        [InlineKeyboardButton(cancel_text, callback_data='cancel_appointment')],
        [InlineKeyboardButton(menu_text, callback_data='back_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_maternal_keyboard(language: str):
    calc_text = '🤰 Pregnancy Week Calculator' if language == 'en' else '🤰 गर्भावस्था सप्ताह कैलकुलेटर' if language == 'hi' else '🤰 ગર્ભાવસ્થા અઠવાડિયું કેલ્ક્યુલેટર'
    growth_text = '👩‍🍼 Baby Growth Tracker' if language == 'en' else '👩‍🍼 बच्चे की वृद्धि ट्रैकर' if language == 'hi' else '👩‍🍼 બાળક વૃદ્ધિ ટ્રેકર'
    schemes_text = '🌿 Gujarat Mother Schemes' if language == 'en' else '🌿 गुजरात माँ योजनाएं' if language == 'hi' else '🌿 ગુજરાત માતા યોજનાઓ'
    menu_text = '🏠 Back to Main Menu' if language == 'en' else '🏠 मुख्य मेनू पर वापस' if language == 'hi' else '🏠 મુખ્ય મેનૂ પર પાછા'
    keyboard = [
        [InlineKeyboardButton(calc_text, callback_data='pregnancy_calc')],
        [InlineKeyboardButton(growth_text, callback_data='baby_growth')],
        [InlineKeyboardButton(schemes_text, callback_data='mother_schemes')],
        [InlineKeyboardButton(menu_text, callback_data='back_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_worker_keyboard(language: str):
    register_text = '📝 Register as Health Worker' if language == 'en' else '📝 स्वास्थ्य कार्यकर्ता के रूप में पंजीकरण करें' if language == 'hi' else '📝 આરોગ્ય કાર્યકર તરીકે નોંધણી કરો'
    patients_text = '📍 My Patients Nearby' if language == 'en' else '📍 मेरे आस-पास के मरीज' if language == 'hi' else '📍 મારા નજીકના દર્દીઓ'
    schedule_text = '📋 Today\'s Schedule' if language == 'en' else '📋 आज का कार्यक्रम' if language == 'hi' else '📋 આજનું શેડ્યૂલ'
    menu_text = '🏠 Back to Main Menu' if language == 'en' else '🏠 मुख्य मेनू पर वापस' if language == 'hi' else '🏠 મુખ્ય મેનૂ પર પાછા'
    keyboard = [
        [InlineKeyboardButton(register_text, callback_data='worker_register')],
        [InlineKeyboardButton(patients_text, callback_data='worker_patients')],
        [InlineKeyboardButton(schedule_text, callback_data='worker_schedule')],
        [InlineKeyboardButton(menu_text, callback_data='back_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_worker_category_keyboard():
    keyboard = [
        [InlineKeyboardButton('ASHA Worker', callback_data='category_asha')],
        [InlineKeyboardButton('Nurse', callback_data='category_nurse')],
        [InlineKeyboardButton('Physiotherapist', callback_data='category_physio')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_issue_category_keyboard():
    keyboard = [
        [InlineKeyboardButton('👤 User', callback_data='issue_cat_user')],
        [InlineKeyboardButton('👩‍⚕️ Worker', callback_data='issue_cat_worker')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_govt_schemes_keyboard(language: str):
    """Dynamic government schemes keyboard from Supabase"""
    try:
        if supabase and supabase_connected:
            # Fetch active schemes from Supabase (limit to 6 for better UX)
            response = supabase.table('govt_schemes').select('*').eq('active', True).limit(6).execute()
            schemes = response.data
            
            if schemes:
                keyboard = []
                
                # Add scheme buttons dynamically
                for scheme in schemes:
                    # Get title based on language
                    if language == 'hi':
                        title = scheme.get('title_hi') or scheme.get('title_en')
                    elif language == 'gu':
                        title = scheme.get('title_gu') or scheme.get('title_en')
                    else:
                        title = scheme.get('title_en')
                    
                    # Truncate title if too long (Telegram limit)
                    if len(title) > 60:
                        title = title[:57] + '...'
                    
                    keyboard.append([InlineKeyboardButton(title, callback_data=f'scheme_id_{scheme["id"]}')])
                
                # Add back button
                menu_text = '🏠 Back to Main Menu' if language == 'en' else '🏠 मुख्य मेनू पर वापस' if language == 'hi' else '🏠 મુખ્ય મેનૂ પર પાછા'
                keyboard.append([InlineKeyboardButton(menu_text, callback_data='back_menu')])
                
                return InlineKeyboardMarkup(keyboard)
    except Exception as e:
        logger.error(f"Error loading schemes from Supabase: {e}")
    
    # Fallback to hardcoded schemes if Supabase fails
    pmmvy_text = '👶 Matru Vandana (PMMVY)' if language == 'en' else '👶 मातृ वंदना (PMMVY)' if language == 'hi' else '👶 માતૃ વંદના (PMMVY)'
    jssk_text = '🏥 Free Delivery (JSSK)' if language == 'en' else '🏥 मुफ्त प्रसव (JSSK)' if language == 'hi' else '🏥 મફત પ્રસૂતિ (JSSK)'
    ma_amrutam_text = '💰 Gujarat Health Insurance' if language == 'en' else '💰 गुजरात स्वास्थ्य बीमा' if language == 'hi' else '💰 ગુજરાત આરોગ્ય વીમો'
    menu_text = '🏠 Back to Main Menu' if language == 'en' else '🏠 मुख्य मेनू पर वापस' if language == 'hi' else '🏠 મુખ્ય મેનૂ પર પાછા'
    
    keyboard = [
        [InlineKeyboardButton(pmmvy_text, callback_data='scheme_pmmvy')],
        [InlineKeyboardButton(jssk_text, callback_data='scheme_jssk')],
        [InlineKeyboardButton(ma_amrutam_text, callback_data='scheme_ma_amrutam')],
        [InlineKeyboardButton(menu_text, callback_data='back_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_hardcoded_hospitals(lat, lon):
    """Hardcoded fallback hospitals for Anklav area"""
    hardcoded = [
        {"name": "Om Hospital Anklav", "lat": 22.246, "lon": 72.688, "phone": "02692-233210"},
        {"name": "PHC Anklav (Primary Health Centre)", "lat": 22.25, "lon": 72.69, "phone": "108"},
        {"name": "Anand District Hospital", "lat": 22.55, "lon": 72.95, "phone": "02692-252700"}
    ]
    
    hospitals = []
    for h in hardcoded:
        distance = geodesic((lat, lon), (h['lat'], h['lon'])).km
        hospitals.append({
            'name': h['name'],
            'distance': distance,
            'lat': h['lat'],
            'lon': h['lon'],
            'phone': h['phone']
        })
    
    return sorted(hospitals, key=lambda x: x['distance'])[:5]

def search_hospitals_overpass(lat, lon, bbox=None, area_name="Anklav Area"):
    """Search hospitals using Overpass API"""
    print("=== HOSPITAL DEBUG START ===")
    print(f"User location: lat={lat}, lon={lon}")
    print(f"Bbox: {bbox}")
    print(f"Area name: {area_name}")
    
    try:
        if bbox is None:
            bbox = get_bbox_for_location(lat, lon, 10)
            print(f"Calculated bbox: {bbox}")
        
        # Simple test query first
        simple_query = f'[out:json];node["amenity"="hospital"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});out;'
        
        overpass_query = f"""
        [out:json];
        (
          node["amenity"~"hospital|clinic|health_post|pharmacy"]["healthcare"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          way["amenity"~"hospital|clinic|health_post|pharmacy"]["healthcare"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          relation["amenity"~"hospital|clinic|health_post|pharmacy"]["healthcare"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          node["amenity"~"hospital|clinic|health_post"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          way["amenity"~"hospital|clinic|health_post"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        );
        out center;
        """
        
        url = 'http://overpass-api.de/api/interpreter'
        print(f"Overpass URL called: {url}")
        print(f"Query (first 500 chars): {overpass_query[:500]}")
        
        response = requests.get(url, params={'data': overpass_query}, timeout=30)
        
        print(f"Overpass response status: {response.status_code}")
        print(f"Raw JSON response (first 1000 chars): {response.text[:1000]}")
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get('elements', [])
            print(f"Parsed elements count: {len(elements)}")
            
            hospitals = []
            
            for element in elements:
                tags = element.get('tags', {})
                print(f"Element: {element.get('type')}, tags: {tags}")
                
                if 'center' in element:
                    hospital_lat = element['center']['lat']
                    hospital_lon = element['center']['lon']
                elif 'lat' in element:
                    hospital_lat = element['lat']
                    hospital_lon = element['lon']
                else:
                    continue
                
                distance = geodesic((lat, lon), (hospital_lat, hospital_lon)).km
                
                name = tags.get('name', tags.get('amenity', 'Unknown').title())
                healthcare_type = tags.get('healthcare', '')
                amenity = tags.get('amenity', '')
                
                if healthcare_type:
                    full_name = f"{name} ({healthcare_type.replace('_', ' ').title()})"
                elif amenity:
                    full_name = f"{name} ({amenity.replace('_', ' ').title()})"
                else:
                    full_name = name
                
                phone = tags.get('phone', tags.get('contact:phone', None))
                
                hospitals.append({
                    'name': full_name,
                    'distance': distance,
                    'lat': hospital_lat,
                    'lon': hospital_lon,
                    'phone': phone
                })
            
            hospitals = sorted(hospitals, key=lambda x: x['distance'])[:5]
            print(f"Final hospitals count: {len(hospitals)}")
            print("=== HOSPITAL DEBUG END ===")
            
            # Fallback to hardcoded if no results
            if not hospitals:
                print("!!! NO RESULTS - Using hardcoded fallback !!!")
                hospitals = get_hardcoded_hospitals(lat, lon)
            
            return hospitals, area_name
        
    except Exception as e:
        logger.error(f"Overpass API error: {e}")
        print(f"!!! EXCEPTION: {e} !!!")
        print("=== HOSPITAL DEBUG END (ERROR) ===")
        # Return hardcoded hospitals on error
        return get_hardcoded_hospitals(lat, lon), area_name
    
    print("=== HOSPITAL DEBUG END (NO DATA) ===")
    return get_hardcoded_hospitals(lat, lon), area_name

def get_city_info(city_name):
    """Get city coordinates and bbox"""
    city_lower = city_name.lower().strip()
    
    for key in CITY_BBOX:
        if key in city_lower:
            bbox = CITY_BBOX[key]
            lat = (bbox[0] + bbox[2]) / 2
            lon = (bbox[1] + bbox[3]) / 2
            return lat, lon, bbox, city_name.title()
    
    try:
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': f'{city_name}, Gujarat, India',
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'MediMindRural/1.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200 and response.json():
            result = response.json()[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            bbox = get_bbox_for_location(lat, lon, 10)
            return lat, lon, bbox, city_name.title()
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
    
    return None, None, None, None

def format_hospital_results(hospitals, area_name, lang):
    """Format hospital results"""
    if not hospitals:
        return None
    
    response = TEXTS[lang]['hospitals_nearby'].format(area_name) + "\n\n"
    
    for i, h in enumerate(hospitals):
        emoji = NUMBER_EMOJIS[i] if i < len(NUMBER_EMOJIS) else f"{i+1}."
        maps_link = f"https://maps.google.com/?q={h['lat']},{h['lon']}"
        
        response += f"{emoji} {h['name']}\n"
        response += f"📍 {h['distance']:.1f}km | "
        
        if h['phone']:
            response += f"📞 {h['phone']}\n"
        else:
            response += f"📞 Call 108\n"
        
        response += f"🗺️ [Open Google Maps]({maps_link})\n\n"
    
    response += TEXTS[lang]['search_other']
    response += TEXTS[lang]['disclaimer']
    
    return response

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['state'] = None
    await update.message.reply_text(TEXTS['en']['welcome'], reply_markup=get_language_keyboard())

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check X-ray request status"""
    lang = context.user_data.get('language', 'en')
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name or 'Unknown'
    
    try:
        if supabase and supabase_connected:
            # Get user's X-ray requests by patient name (since we don't store user_id)
            # This is a limitation - we'll show recent requests
            response = supabase.table('xray_requests').select('*').order('created_at', desc=True).limit(10).execute()
            
            if response.data and len(response.data) > 0:
                text = TEXTS[lang]['xray_status']
                status_emoji = {'pending': '⏳', 'reviewed': '🔍', 'sent': '✅', 'cancelled': '❌'}
                
                for r in response.data:
                    emoji = status_emoji.get(r.get('status', 'pending'), '❓')
                    text += f"{emoji} {r['patient_name']} ({r['age']}y) - {r.get('status', 'pending')}\n"
                    text += f"   📍 {r.get('village', 'N/A')}\n"
                    if r.get('reviewed_at'):
                        text += f"   ✅ Reviewed: {r['reviewed_at']}\n"
                    text += "\n"
                
                await update.message.reply_text(text, reply_markup=get_main_menu_keyboard(lang))
            else:
                await update.message.reply_text(TEXTS[lang]['no_xray_requests'], reply_markup=get_main_menu_keyboard(lang))
        else:
            await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
    except Exception as e:
        logger.error(f"Status check error: {e}")
        await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith('lang_'):
        lang_code = data.split('_')[1]
        context.user_data['language'] = lang_code
        context.user_data['state'] = None
        await query.edit_message_text(text=TEXTS[lang_code]['main_menu'], reply_markup=get_main_menu_keyboard(lang_code))
    
    elif data == 'change_lang':
        context.user_data['state'] = None
        await query.edit_message_text(text=TEXTS['en']['welcome'], reply_markup=get_language_keyboard())
    
    elif data == 'back_menu':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = None
        await query.edit_message_text(text=TEXTS[lang]['main_menu'], reply_markup=get_main_menu_keyboard(lang))
    
    elif data == 'menu_hospital':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_hospital_input'
        await query.message.reply_text(TEXTS[lang]['hospital_prompt'], reply_markup=get_hospital_search_keyboard(lang))
    
    elif data == 'menu_emergency':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_emergency_location'
        await query.message.reply_text(TEXTS[lang]['emergency_prompt'], reply_markup=get_emergency_keyboard(lang))
    
    elif data == 'menu_medicine':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = None
        await query.edit_message_text(TEXTS[lang]['medicine_menu'], reply_markup=get_medicine_keyboard(lang))
    
    elif data == 'menu_visit':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = None
        await query.edit_message_text(TEXTS[lang]['visit_menu'], reply_markup=get_visit_keyboard(lang))
    
    elif data == 'menu_maternal':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = None
        await query.edit_message_text(TEXTS[lang]['maternal_menu'], reply_markup=get_maternal_keyboard(lang))
    
    elif data == 'menu_xray_check':
        lang = context.user_data.get('language', 'en')
        keyboard = [[InlineKeyboardButton("✅ I consent", callback_data="xray_consent_yes")],
                    [InlineKeyboardButton("🔙 Back", callback_data="back_menu")]]
        await query.edit_message_text(TEXTS[lang]['xray_consent'], reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'xray_consent_yes':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_xray_name'
        context.user_data['patient_form'] = {}  # Initialize form
        await query.message.reply_text("👤 Enter patient name:", reply_markup=ReplyKeyboardRemove())
    
    elif data.startswith('xray_doctor_'):
        doctor_phone = data.replace('xray_doctor_', '')
        lang = context.user_data.get('language', 'en')
        form = context.user_data.get('patient_form', {})
        
        try:
            if supabase and supabase_connected:
                # Get current timestamp
                from datetime import datetime as dt
                current_time = dt.now().isoformat()
                
                # Insert X-ray request with image PATH (not file_id)
                request_data = {
                    'patient_name': form.get('name'),
                    'age': form.get('age'),
                    'village': form.get('village'),
                    'symptoms': form.get('symptoms'),
                    'doctor_phone': doctor_phone,
                    'image_url': form.get('image_path', ''),  # Store local file path
                    'status': 'pending',
                    'consent_time': current_time,
                    'patient_telegram_id': update.effective_user.id  # Store patient's telegram ID
                }
                response = supabase.table('xray_requests').insert(request_data).execute()
                request_id = response.data[0]['id'] if response.data else None
                
                # Get doctor's telegram_id to notify
                doctor_response = supabase.table('doctors').select('telegram_id, name').eq('phone', doctor_phone).execute()
                
                if doctor_response.data and len(doctor_response.data) > 0:
                    doctor = doctor_response.data[0]
                    doctor_telegram_id = doctor.get('telegram_id')
                    
                    # Notify doctor with image from local file
                    if doctor_telegram_id:
                        try:
                            # Send notification via DOCTOR bot (not patient bot)
                            image_path = form.get('image_path')
                            
                            # Create inline keyboard with buttons
                            keyboard = {
                                'inline_keyboard': [
                                    [{'text': '📥 Requests', 'callback_data': 'requests'}],
                                    [{'text': '🔙 Main Menu', 'callback_data': 'back_menu'}]
                                ]
                            }
                            
                            if image_path and os.path.exists(image_path):
                                # Send photo via doctor bot with buttons
                                with open(image_path, 'rb') as photo_file:
                                    files = {'photo': photo_file}
                                    data = {
                                        'chat_id': doctor_telegram_id,
                                        'caption': f"🩻 **NEW X-RAY REQUEST** (ID: {request_id})\n\n"
                                                  f"👤 {form['name']} ({form['age']}y)\n"
                                                  f"📍 {form['village']}\n"
                                                  f"🩺 {form['symptoms']}\n\n"
                                                  f"📥 Click 'Requests' button below to analyze",
                                        'parse_mode': 'Markdown',
                                        'reply_markup': json.dumps(keyboard)
                                    }
                                    response = requests.post(
                                        f"https://api.telegram.org/bot{DOCTOR_BOT_TOKEN}/sendPhoto",
                                        data=data,
                                        files=files
                                    )
                                    if response.status_code == 200:
                                        logger.info(f"Notification sent to doctor {doctor_telegram_id} via @MediMindDoctorBot")
                                    else:
                                        logger.error(f"Failed to send notification: {response.text}")
                            else:
                                # Fallback if no image
                                response = requests.post(
                                    f"https://api.telegram.org/bot{DOCTOR_BOT_TOKEN}/sendMessage",
                                    json={
                                        'chat_id': doctor_telegram_id,
                                        'text': f"🩻 NEW X-RAY REQUEST (ID: {request_id})\n\n"
                                               f"👤 {form['name']} ({form['age']}y)\n"
                                               f"📍 {form['village']}\n"
                                               f"🩺 {form['symptoms']}\n\n"
                                               f"📋 Click 'Requests' button below to analyze",
                                        'parse_mode': 'Markdown',
                                        'reply_markup': keyboard
                                    }
                                )
                        except Exception as e:
                            logger.error(f"Failed to notify doctor: {e}")
                
                # Don't clean up image - doctor needs it!
                # image_path will be used by doctor bot
                
                await query.edit_message_text(TEXTS[lang]['xray_sent'], reply_markup=get_main_menu_keyboard(lang))
                context.user_data.pop('patient_form', None)
                context.user_data['state'] = None
            else:
                await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"X-ray request error: {e}")
            await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
    
    elif data == 'menu_schemes':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = None
        await query.edit_message_text(TEXTS[lang]['govt_schemes_menu'], reply_markup=get_govt_schemes_keyboard(lang))
    
    elif data.startswith('scheme_id_'):
        # Dynamic scheme handler - loads from Supabase
        scheme_id = int(data.split('_')[2])
        lang = context.user_data.get('language', 'en')
        
        try:
            if supabase and supabase_connected:
                # Fetch scheme details from Supabase
                response = supabase.table('govt_schemes').select('*').eq('id', scheme_id).execute()
                
                if response.data:
                    scheme = response.data[0]
                    
                    # Get content based on language
                    if lang == 'hi':
                        title = scheme.get('title_hi') or scheme.get('title_en')
                        desc = scheme.get('desc_hi') or scheme.get('desc_en')
                    elif lang == 'gu':
                        title = scheme.get('title_gu') or scheme.get('title_en')
                        desc = scheme.get('desc_gu') or scheme.get('desc_en')
                    else:
                        title = scheme.get('title_en')
                        desc = scheme.get('desc_en')
                    
                    # Format message
                    message = f"🌿 {title}\n\n{desc}"
                    
                    if scheme.get('phone'):
                        message += f"\n\n📞 Helpline: {scheme['phone']}"
                    
                    if scheme.get('link'):
                        message += f"\n🔗 More Info: {scheme['link']}"
                    
                    await query.message.reply_text(message, reply_markup=get_govt_schemes_keyboard(lang))
                else:
                    await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_govt_schemes_keyboard(lang))
            else:
                await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_govt_schemes_keyboard(lang))
        except Exception as e:
            logger.error(f"Error loading scheme {scheme_id}: {e}")
            await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_govt_schemes_keyboard(lang))
    
    elif data == 'scheme_pmmvy':
        # Fallback for old hardcoded scheme
        lang = context.user_data.get('language', 'en')
        await query.message.reply_text(TEXTS[lang]['scheme_pmmvy'], reply_markup=get_govt_schemes_keyboard(lang))
    
    elif data == 'scheme_jssk':
        # Fallback for old hardcoded scheme
        lang = context.user_data.get('language', 'en')
        await query.message.reply_text(TEXTS[lang]['scheme_jssk'], reply_markup=get_govt_schemes_keyboard(lang))
    
    elif data == 'scheme_ma_amrutam':
        # Fallback for old hardcoded scheme
        lang = context.user_data.get('language', 'en')
        await query.message.reply_text(TEXTS[lang]['scheme_ma_amrutam'], reply_markup=get_govt_schemes_keyboard(lang))
    
    elif data == 'scheme_all_list':
        # Fallback for old hardcoded scheme
        lang = context.user_data.get('language', 'en')
        await query.message.reply_text(TEXTS[lang]['scheme_all_list'], reply_markup=get_govt_schemes_keyboard(lang))
    
    elif data == 'menu_raise_problem':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_issue_name'
        await query.message.reply_text(TEXTS[lang]['issue_name_prompt'], reply_markup=ReplyKeyboardRemove())
    
    elif data.startswith('issue_cat_'):
        category = data.split('_')[2].capitalize()
        context.user_data['issue_category'] = category
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_issue_age'
        await query.message.reply_text(TEXTS[lang]['issue_age_prompt'], reply_markup=ReplyKeyboardRemove())
    
    elif data == 'menu_worker':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = None
        await query.edit_message_text(TEXTS[lang]['worker_menu'], reply_markup=get_worker_keyboard(lang))
    
    elif data == 'worker_register':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_worker_name'
        await query.message.reply_text(TEXTS[lang]['worker_register_name'], reply_markup=ReplyKeyboardRemove())
    
    elif data.startswith('category_'):
        category = data.split('_')[1].upper()
        context.user_data['worker_category'] = category
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_worker_experience'
        await query.message.reply_text(TEXTS[lang]['worker_register_experience'], reply_markup=ReplyKeyboardRemove())
    
    elif data == 'worker_patients':
        lang = context.user_data.get('language', 'en')
        user_id = query.from_user.id
        
        try:
            if supabase and supabase_connected:
                # Check if user is approved worker
                worker_response = supabase.table('health_workers').select('*').eq('user_id', user_id).eq('approved', True).execute()
                
                if not worker_response.data:
                    await query.message.reply_text(TEXTS[lang]['worker_not_approved'], reply_markup=get_worker_keyboard(lang))
                    return
                
                # Get reminders
                reminders_response = supabase.table('reminders').select('*').eq('active', True).limit(5).execute()
                # Get appointments
                appointments_response = supabase.table('appointments').select('*').limit(5).execute()
                # Get emergencies
                emergencies_response = supabase.table('emergencies').select('*').eq('status', 'pending').execute()
                
                text = TEXTS[lang]['worker_patients']
                
                if reminders_response.data:
                    for r in reminders_response.data:
                        text += f"👤 {r['username']} - {r['medicine_name']} reminder\n"
                
                if appointments_response.data:
                    for a in appointments_response.data:
                        text += f"👤 {a['username']} - {a['hospital']} visit {a['date']}\n"
                
                text += f"\n{TEXTS[lang]['worker_emergencies']}"
                text += f"🚨 {len(emergencies_response.data)} Emergencies pending\n"
                
                await query.message.reply_text(text, reply_markup=get_worker_keyboard(lang))
            else:
                await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Worker patients error: {e}")
            await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
    
    elif data == 'worker_schedule':
        lang = context.user_data.get('language', 'en')
        user_id = query.from_user.id
        from datetime import datetime
        today = datetime.now().strftime('%d-%m-%Y')
        
        try:
            if supabase and supabase_connected:
                # Check if user is approved worker
                worker_response = supabase.table('health_workers').select('*').eq('user_id', user_id).eq('approved', True).execute()
                
                if not worker_response.data:
                    await query.message.reply_text(TEXTS[lang]['worker_not_approved'], reply_markup=get_worker_keyboard(lang))
                    return
                
                appointments_response = supabase.table('appointments').select('*').eq('date', today).execute()
                
                if appointments_response.data:
                    text = f"📋 Today's Schedule ({today}):\n\n"
                    for a in appointments_response.data:
                        text += f"⏰ {a['time']} - {a['username']} at {a['hospital']}\n"
                    await query.message.reply_text(text, reply_markup=get_worker_keyboard(lang))
                else:
                    await query.message.reply_text(TEXTS[lang]['no_patients'], reply_markup=get_worker_keyboard(lang))
            else:
                await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Worker schedule error: {e}")
            await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
    
    elif data == 'pregnancy_calc':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_lmp_date'
        await query.message.reply_text(TEXTS[lang]['lmp_prompt'], reply_markup=ReplyKeyboardRemove())
    
    elif data == 'baby_growth':
        lang = context.user_data.get('language', 'en')
        await query.message.reply_text(TEXTS[lang]['growth_info'], reply_markup=get_maternal_keyboard(lang))
    
    elif data == 'mother_schemes':
        lang = context.user_data.get('language', 'en')
        await query.message.reply_text(TEXTS[lang]['schemes_info'], reply_markup=get_maternal_keyboard(lang))
    
    elif data == 'new_reminder':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_medicine_name'
        await query.message.reply_text(TEXTS[lang]['medicine_prompt'], reply_markup=ReplyKeyboardRemove())
    
    elif data == 'list_reminders':
        lang = context.user_data.get('language', 'en')
        user_id = query.from_user.id
        
        try:
            if supabase and supabase_connected:
                response = supabase.table('reminders').select('*').eq('user_id', user_id).eq('active', True).execute()
                reminders = response.data
                
                if reminders:
                    text = TEXTS[lang]['list_reminders'] + '\n\n'
                    for i, r in enumerate(reminders, 1):
                        text += f"{i}. 💊 {r['medicine_name']}\n   ⏰ {r['time']}\n   📋 {r['dosage']}\n\n"
                    await query.message.reply_text(text, reply_markup=get_medicine_keyboard(lang))
                else:
                    await query.message.reply_text(TEXTS[lang]['no_reminders'], reply_markup=get_medicine_keyboard(lang))
            else:
                await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"List reminders error: {e}")
            await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
    
    elif data == 'delete_reminder':
        lang = context.user_data.get('language', 'en')
        user_id = query.from_user.id
        
        try:
            if supabase and supabase_connected:
                response = supabase.table('reminders').select('*').eq('user_id', user_id).eq('active', True).execute()
                reminders = response.data
                
                if reminders:
                    text = TEXTS[lang]['delete_prompt'] + '\n\n'
                    for i, r in enumerate(reminders, 1):
                        text += f"{i}. {r['medicine_name']} - {r['time']}\n"
                    context.user_data['state'] = 'waiting_reminder_delete'
                    await query.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
                else:
                    await query.message.reply_text(TEXTS[lang]['no_reminders'], reply_markup=get_medicine_keyboard(lang))
            else:
                await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Delete reminder error: {e}")
            await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
    
    elif data == 'new_appointment':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_appointment_hospital'
        await query.message.reply_text(TEXTS[lang]['appointment_hospital'], reply_markup=ReplyKeyboardRemove())
    
    elif data == 'list_appointments':
        lang = context.user_data.get('language', 'en')
        user_id = query.from_user.id
        
        try:
            if supabase and supabase_connected:
                response = supabase.table('appointments').select('*').eq('user_id', user_id).execute()
                appointments = response.data
                
                if appointments:
                    text = TEXTS[lang]['list_appointments'] + '\n\n'
                    for i, a in enumerate(appointments, 1):
                        text += f"{i}. 📅 {a['date']} at {a['time']}\n   🏥 {a['hospital']}\n   📝 {a['notes']}\n\n"
                    await query.message.reply_text(text, reply_markup=get_visit_keyboard(lang))
                else:
                    await query.message.reply_text(TEXTS[lang]['no_appointments'], reply_markup=get_visit_keyboard(lang))
            else:
                await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"List appointments error: {e}")
            await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
    
    elif data == 'cancel_appointment':
        lang = context.user_data.get('language', 'en')
        user_id = query.from_user.id
        
        try:
            if supabase and supabase_connected:
                response = supabase.table('appointments').select('*').eq('user_id', user_id).execute()
                appointments = response.data
                
                if appointments:
                    text = TEXTS[lang]['cancel_appointment_prompt'] + '\n\n'
                    for i, a in enumerate(appointments, 1):
                        text += f"{i}. {a['date']} - {a['hospital']}\n"
                    context.user_data['state'] = 'waiting_appointment_cancel'
                    await query.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
                else:
                    await query.message.reply_text(TEXTS[lang]['no_appointments'], reply_markup=get_visit_keyboard(lang))
            else:
                await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Cancel appointment error: {e}")
            await query.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
    
    elif data == 'search_city':
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = 'waiting_city_name'
        await query.message.reply_text(TEXTS[lang]['enter_city'], reply_markup=ReplyKeyboardRemove())
    
    elif data.startswith('menu_'):
        lang = context.user_data.get('language', 'en')
        context.user_data['state'] = None
        await query.edit_message_text(text=TEXTS[lang]['coming_soon'], reply_markup=get_change_language_keyboard(lang))

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = context.user_data.get('language', 'en')
    state = context.user_data.get('state')
    
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        
        # Worker registration location handling
        if state == 'waiting_worker_location':
            await update.message.reply_text('📝 Processing registration...', reply_markup=ReplyKeyboardRemove())
            
            try:
                user_id = update.message.from_user.id
                username = update.message.from_user.username or update.message.from_user.first_name or 'Unknown'
                
                worker_name = context.user_data.get('worker_name')
                worker_age = context.user_data.get('worker_age')
                worker_category = context.user_data.get('worker_category')
                worker_experience = context.user_data.get('worker_experience')
                
                # Save to Supabase
                if supabase and supabase_connected:
                    try:
                        worker_data = {
                            'user_id': user_id,
                            'username': username,
                            'name': worker_name,
                            'age': worker_age,
                            'category': worker_category,
                            'experience': worker_experience,
                            'lat': lat,
                            'lon': lon,
                            'approved': False
                        }
                        print(f"Inserting worker to Supabase: {worker_data}")
                        response = supabase.table('health_workers').insert(worker_data).execute()
                        print(f"✅ Worker registration saved: {response}")
                        
                        # Send to admin for approval
                        if ADMIN_ID:
                            maps_link = f"https://maps.google.com/?q={lat},{lon}"
                            admin_message = f"👩‍⚕️ NEW HEALTH WORKER REGISTRATION\n\n👤 Name: {worker_name}\n🎂 Age: {worker_age}\n🏷️ Category: {worker_category}\n📅 Experience: {worker_experience} years\n📱 User: @{username} (ID: {user_id})\n📍 Location: {lat}, {lon}\n🗺️ {maps_link}\n\n⚠️ Please approve in Supabase dashboard"
                            
                            try:
                                await context.bot.send_location(chat_id=ADMIN_ID, latitude=lat, longitude=lon)
                                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
                                print(f"✅ Sent registration to admin: {ADMIN_ID}")
                            except Exception as e:
                                print(f"❌ Failed to send to admin: {e}")
                                logger.error(f"Failed to send to admin: {e}")
                        
                        await update.message.reply_text(TEXTS[lang]['worker_registration_sent'], reply_markup=get_main_menu_keyboard(lang))
                    except Exception as e:
                        print(f"❌ Worker registration error: {e}")
                        logger.error(f"Worker registration error: {e}")
                        await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
                else:
                    await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
                    
            except Exception as e:
                logger.error(f"Worker registration handler error: {e}")
                print(f"❌ Worker registration handler error: {e}")
                await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
            
            context.user_data['state'] = None
            return
        
        # Emergency location handling
        if state == 'waiting_emergency_location':
            await update.message.reply_text('🚨 Processing emergency...', reply_markup=ReplyKeyboardRemove())
            
            try:
                user_id = update.message.from_user.id
                username = update.message.from_user.username or update.message.from_user.first_name or 'Unknown'
                
                print(f"=== EMERGENCY DEBUG ===")
                print(f"User: {username} (ID: {user_id})")
                print(f"Location: {lat}, {lon}")
                
                # Save to Supabase
                if supabase and supabase_connected:
                    try:
                        emergency_data = {
                            'user_id': user_id,
                            'username': username,
                            'lat': lat,
                            'lon': lon,
                            'status': 'pending'
                        }
                        print(f"Inserting to Supabase: {emergency_data}")
                        response = supabase.table('emergencies').insert(emergency_data).execute()
                        print(f"✅ Supabase insert response: {response}")
                    except Exception as e:
                        print(f"❌ Supabase insert error: {e}")
                        logger.error(f"Supabase insert error: {e}")
                else:
                    print("⚠️ Supabase not available, skipping database save")
                
                # Send to admin (always try this)
                if ADMIN_ID:
                    maps_link = f"https://maps.google.com/?q={lat},{lon}"
                    admin_message = f"🚨 EMERGENCY ALERT!\n\n👤 User: @{username} (ID: {user_id})\n📍 Location: {lat}, {lon}\n🗺️ {maps_link}\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    try:
                        await context.bot.send_location(chat_id=ADMIN_ID, latitude=lat, longitude=lon)
                        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
                        print(f"✅ Sent to admin: {ADMIN_ID}")
                    except Exception as e:
                        print(f"❌ Failed to send to admin: {e}")
                        logger.error(f"Failed to send to admin: {e}")
                else:
                    print("⚠️ ADMIN_ID not set")
                
                print(f"=== EMERGENCY DEBUG END ===")
                
                # Reply to user
                maps_link = f"https://maps.google.com/?q={lat},{lon}"
                response = TEXTS[lang]['sos_sent'].format(maps_link)
                await update.message.reply_text(response, parse_mode='Markdown', reply_markup=get_main_menu_keyboard(lang))
                
            except Exception as e:
                logger.error(f"Emergency save error: {e}")
                print(f"❌ Emergency handler error: {e}")
                await update.message.reply_text(TEXTS[lang]['sos_error'], reply_markup=get_main_menu_keyboard(lang))
            
            context.user_data['state'] = None
            return
        
        # Hospital location handling
        await update.message.reply_text(TEXTS[lang]['searching'], reply_markup=ReplyKeyboardRemove())
        
        bbox = get_bbox_for_location(lat, lon, 10)
        hospitals, area_name = search_hospitals_overpass(lat, lon, bbox, "Your Location")
        
        if not hospitals:
            lat, lon = 22.246, 72.688
            bbox = (22.1, 72.5, 22.4, 72.9)
            hospitals, area_name = search_hospitals_overpass(lat, lon, bbox, "Anklav Area")
        
        if hospitals:
            response = format_hospital_results(hospitals, area_name, lang)
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=get_hospital_results_keyboard(lang))
        else:
            await update.message.reply_text(TEXTS[lang]['no_hospitals'], reply_markup=get_main_menu_keyboard(lang))
        
        context.user_data['state'] = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = context.user_data.get('language', 'en')
    state = context.user_data.get('state')
    text = update.message.text
    
    # Handle emergency cancel
    if state == 'waiting_emergency_location' and ('❌' in text or 'Cancel' in text or 'रद्द' in text or 'રદ' in text):
        context.user_data['state'] = None
        await update.message.reply_text(TEXTS[lang]['emergency_cancel'], reply_markup=get_main_menu_keyboard(lang))
        return
    
    if '🔍' in text and ('Search' in text or 'खोजें' in text or 'શોધો' in text):
        context.user_data['state'] = 'waiting_city_name'
        await update.message.reply_text(TEXTS[lang]['enter_city'], reply_markup=ReplyKeyboardRemove())
        return
    
    if state == 'waiting_city_name':
        city_name = text
        await update.message.reply_text(TEXTS[lang]['searching'])
        
        lat, lon, bbox, area_name = get_city_info(city_name)
        
        if not lat or not lon:
            lat, lon = 22.246, 72.688
            bbox = (22.1, 72.5, 22.4, 72.9)
            area_name = "Anklav Area"
        
        hospitals, area_name = search_hospitals_overpass(lat, lon, bbox, area_name)
        
        if hospitals:
            response = format_hospital_results(hospitals, area_name, lang)
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=get_hospital_results_keyboard(lang))
        else:
            await update.message.reply_text(TEXTS[lang]['no_hospitals'], reply_markup=get_main_menu_keyboard(lang))
        
        context.user_data['state'] = None
    
    elif state == 'waiting_medicine_name':
        context.user_data['medicine_name'] = text
        context.user_data['state'] = 'waiting_medicine_time'
        await update.message.reply_text(TEXTS[lang]['medicine_time'])
    
    elif state == 'waiting_medicine_time':
        context.user_data['medicine_time'] = text
        context.user_data['state'] = 'waiting_medicine_dosage'
        await update.message.reply_text(TEXTS[lang]['medicine_dosage'])
    
    elif state == 'waiting_medicine_dosage':
        dosage = text
        medicine_name = context.user_data.get('medicine_name')
        medicine_time = context.user_data.get('medicine_time')
        user_id = update.message.from_user.id
        username = update.message.from_user.username or update.message.from_user.first_name or 'Unknown'
        
        try:
            if supabase and supabase_connected:
                reminder_data = {
                    'user_id': user_id,
                    'username': username,
                    'medicine_name': medicine_name,
                    'time': medicine_time,
                    'dosage': dosage,
                    'active': True
                }
                supabase.table('reminders').insert(reminder_data).execute()
                
                response = TEXTS[lang]['reminder_set'].format(medicine_name, medicine_time, dosage)
                await update.message.reply_text(response, reply_markup=get_medicine_keyboard(lang))
            else:
                await update.message.reply_text(TEXTS[lang]['reminder_error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Reminder save error: {e}")
            await update.message.reply_text(TEXTS[lang]['reminder_error'], reply_markup=get_main_menu_keyboard(lang))
        
        context.user_data['state'] = None
    
    elif state == 'waiting_reminder_delete':
        try:
            reminder_num = int(text)
            user_id = update.message.from_user.id
            
            if supabase and supabase_connected:
                response = supabase.table('reminders').select('*').eq('user_id', user_id).eq('active', True).execute()
                reminders = response.data
                
                if 0 < reminder_num <= len(reminders):
                    reminder_id = reminders[reminder_num - 1]['id']
                    supabase.table('reminders').update({'active': False}).eq('id', reminder_id).execute()
                    await update.message.reply_text(TEXTS[lang]['reminder_stopped'], reply_markup=get_medicine_keyboard(lang))
                else:
                    await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_medicine_keyboard(lang))
            else:
                await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
        except:
            await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_medicine_keyboard(lang))
        
        context.user_data['state'] = None
    
    elif state == 'waiting_appointment_hospital':
        context.user_data['appointment_hospital'] = text
        context.user_data['state'] = 'waiting_appointment_date'
        await update.message.reply_text(TEXTS[lang]['appointment_date'])
    
    elif state == 'waiting_appointment_date':
        context.user_data['appointment_date'] = text
        context.user_data['state'] = 'waiting_appointment_time'
        await update.message.reply_text(TEXTS[lang]['appointment_time'])
    
    elif state == 'waiting_appointment_time':
        context.user_data['appointment_time'] = text
        context.user_data['state'] = 'waiting_appointment_notes'
        await update.message.reply_text(TEXTS[lang]['appointment_notes'])
    
    elif state == 'waiting_appointment_notes':
        notes = text
        hospital = context.user_data.get('appointment_hospital')
        date = context.user_data.get('appointment_date')
        time = context.user_data.get('appointment_time')
        user_id = update.message.from_user.id
        username = update.message.from_user.username or update.message.from_user.first_name or 'Unknown'
        
        try:
            if supabase and supabase_connected:
                appointment_data = {
                    'user_id': user_id,
                    'username': username,
                    'hospital': hospital,
                    'date': date,
                    'time': time,
                    'notes': notes,
                    'reminder_sent': False
                }
                supabase.table('appointments').insert(appointment_data).execute()
                
                response = TEXTS[lang]['appointment_booked'].format(hospital, date, time, notes)
                await update.message.reply_text(response, reply_markup=get_visit_keyboard(lang))
            else:
                await update.message.reply_text(TEXTS[lang]['appointment_error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Appointment save error: {e}")
            await update.message.reply_text(TEXTS[lang]['appointment_error'], reply_markup=get_main_menu_keyboard(lang))
        
        context.user_data['state'] = None
    
    elif state == 'waiting_xray_name':
        # Step 1: Get patient name
        context.user_data['patient_form']['name'] = text
        context.user_data['state'] = 'waiting_xray_age'
        await update.message.reply_text("🎂 Enter patient age:")
    
    elif state == 'waiting_xray_age':
        # Step 2: Get patient age
        try:
            age = int(text)
            if age <= 0 or age >= 120:
                await update.message.reply_text("❌ Invalid age! Please enter age between 1-119:")
                return
            context.user_data['patient_form']['age'] = age
            context.user_data['state'] = 'waiting_xray_village'
            await update.message.reply_text("📍 Enter village/city name:")
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number for age:")
    
    elif state == 'waiting_xray_village':
        # Step 3: Get village
        context.user_data['patient_form']['village'] = text
        context.user_data['state'] = 'waiting_xray_symptoms'
        await update.message.reply_text("🩺 Describe symptoms:\n\nExample: Cough 5 days, chest pain, fever")
    
    elif state == 'waiting_xray_symptoms':
        # Step 4: Get symptoms, then ask for image
        context.user_data['patient_form']['symptoms'] = text
        context.user_data['state'] = 'waiting_xray_image'
        
        await update.message.reply_text(
            "📸 **Upload X-Ray Image**\n\n"
            "Please send the X-ray image now.\n\n"
            "📱 You can take a photo or send from gallery.",
            parse_mode='Markdown'
        )
    
    elif state == 'waiting_xray_form':
        # Parse X-ray form: Name|Age|Village|Symptoms
        parts = [p.strip() for p in text.split('|')]
        
        if len(parts) >= 4:
            patient_name, age, village, symptoms = parts[0], parts[1], parts[2], parts[3]
            
            try:
                age_int = int(age)
                
                # Store form data
                context.user_data['patient_form'] = {
                    'name': patient_name,
                    'age': age_int,
                    'village': village,
                    'symptoms': symptoms
                }
                
                # Get available doctors from Supabase
                if supabase and supabase_connected:
                    doctors_response = supabase.table('doctors').select('phone, name, phc, rating').eq('active', True).order('rating', desc=True).limit(5).execute()
                    
                    if doctors_response.data and len(doctors_response.data) > 0:
                        keyboard = []
                        for doc in doctors_response.data:
                            rating_stars = '⭐' * int(doc.get('rating', 0))
                            btn_text = f"Dr. {doc['name']} {rating_stars} ({doc.get('phc', 'PHC')})"
                            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"xray_doctor_{doc['phone']}")])
                        keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data="back_menu")])
                        
                        await update.message.reply_text(
                            TEXTS[lang]['xray_doctor_select'].format(patient_name, age, village),
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                    else:
                        await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
                else:
                    await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
                
            except ValueError:
                await update.message.reply_text(TEXTS[lang]['xray_form_error'], reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text(TEXTS[lang]['xray_form_error'], reply_markup=ReplyKeyboardRemove())
    
    elif state == 'waiting_appointment_cancel':
        try:
            appointment_num = int(text)
            user_id = update.message.from_user.id
            
            if supabase and supabase_connected:
                response = supabase.table('appointments').select('*').eq('user_id', user_id).execute()
                appointments = response.data
                
                if 0 < appointment_num <= len(appointments):
                    appointment_id = appointments[appointment_num - 1]['id']
                    supabase.table('appointments').delete().eq('id', appointment_id).execute()
                    await update.message.reply_text(TEXTS[lang]['appointment_cancelled'], reply_markup=get_visit_keyboard(lang))
                else:
                    await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_visit_keyboard(lang))
            else:
                await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
        except:
            await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_visit_keyboard(lang))
        
        context.user_data['state'] = None
    
    elif state == 'waiting_lmp_date':
        try:
            from datetime import datetime, timedelta
            
            lmp_date_str = text
            lmp_date = datetime.strptime(lmp_date_str, '%d-%m-%Y')
            today = datetime.now()
            
            # Calculate weeks pregnant
            days_diff = (today - lmp_date).days
            weeks_pregnant = days_diff // 7
            
            # Calculate due date (280 days from LMP)
            due_date = lmp_date + timedelta(days=280)
            due_date_str = due_date.strftime('%d-%m-%Y')
            
            # Calculate next ANC visit (every 4 weeks until week 28)
            if weeks_pregnant < 28:
                next_visit_weeks = ((weeks_pregnant // 4) + 1) * 4
                next_visit_date = lmp_date + timedelta(weeks=next_visit_weeks)
            else:
                next_visit_date = today + timedelta(weeks=2)
            next_visit_str = next_visit_date.strftime('%d-%m-%Y')
            
            # Save to Supabase
            user_id = update.message.from_user.id
            username = update.message.from_user.username or update.message.from_user.first_name or 'Unknown'
            
            if supabase and supabase_connected:
                try:
                    maternal_data = {
                        'user_id': user_id,
                        'username': username,
                        'lmp_date': lmp_date_str,
                        'weeks_pregnant': weeks_pregnant,
                        'due_date': due_date_str
                    }
                    supabase.table('maternal').insert(maternal_data).execute()
                except Exception as e:
                    logger.error(f"Maternal save error: {e}")
            
            response = TEXTS[lang]['pregnancy_result'].format(lmp_date_str, weeks_pregnant, due_date_str, next_visit_str)
            await update.message.reply_text(response, reply_markup=get_maternal_keyboard(lang))
            
        except ValueError:
            await update.message.reply_text(TEXTS[lang]['maternal_error'], reply_markup=get_maternal_keyboard(lang))
        
        context.user_data['state'] = None
    
    elif state == 'waiting_worker_name':
        worker_name = text
        context.user_data['worker_name'] = worker_name
        context.user_data['state'] = 'waiting_worker_age'
        lang = context.user_data.get('language', 'en')
        await update.message.reply_text(TEXTS[lang]['worker_register_age'])
    
    elif state == 'waiting_worker_age':
        try:
            worker_age = int(text)
            context.user_data['worker_age'] = worker_age
            context.user_data['state'] = 'waiting_worker_category'
            lang = context.user_data.get('language', 'en')
            await update.message.reply_text(TEXTS[lang]['worker_register_category'], reply_markup=get_worker_category_keyboard())
        except ValueError:
            lang = context.user_data.get('language', 'en')
            await update.message.reply_text(TEXTS[lang]['error'])
    
    elif state == 'waiting_worker_experience':
        try:
            worker_experience = int(text)
            context.user_data['worker_experience'] = worker_experience
            context.user_data['state'] = 'waiting_worker_location'
            lang = context.user_data.get('language', 'en')
            
            # Create location share keyboard
            share_text = '📍 Share Location' if lang == 'en' else '📍 स्थान साझा करें' if lang == 'hi' else '📍 સ્થાન શેર કરો'
            keyboard = [[KeyboardButton(share_text, request_location=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(TEXTS[lang]['worker_register_location'], reply_markup=reply_markup)
        except ValueError:
            lang = context.user_data.get('language', 'en')
            await update.message.reply_text(TEXTS[lang]['error'])
    
    elif state == 'waiting_issue_name':
        issue_name = text
        context.user_data['issue_name'] = issue_name
        context.user_data['state'] = 'waiting_issue_category'
        lang = context.user_data.get('language', 'en')
        await update.message.reply_text(TEXTS[lang]['issue_category_prompt'], reply_markup=get_issue_category_keyboard())
    
    elif state == 'waiting_issue_age':
        try:
            issue_age = int(text)
            context.user_data['issue_age'] = issue_age
            context.user_data['state'] = 'waiting_issue_description'
            lang = context.user_data.get('language', 'en')
            await update.message.reply_text(TEXTS[lang]['issue_description_prompt'])
        except ValueError:
            lang = context.user_data.get('language', 'en')
            await update.message.reply_text(TEXTS[lang]['error'])
    
    elif state == 'waiting_issue_description':
        description = text
        issue_name = context.user_data.get('issue_name')
        issue_category = context.user_data.get('issue_category')
        issue_age = context.user_data.get('issue_age')
        user_id = update.message.from_user.id
        username = update.message.from_user.username or update.message.from_user.first_name or 'Unknown'
        lang = context.user_data.get('language', 'en')
        
        try:
            if supabase and supabase_connected:
                issue_data = {
                    'user_id': user_id,
                    'username': username,
                    'name': issue_name,
                    'category': issue_category,
                    'age': issue_age,
                    'description': description,
                    'status': 'open'
                }
                supabase.table('issues').insert(issue_data).execute()
                
                # Send to admin
                if ADMIN_ID:
                    admin_message = f"📢 NEW PROBLEM REPORTED\n\n👤 Name: {issue_name}\n🏷️ Category: {issue_category}\n🎂 Age: {issue_age}\n📱 User: @{username} (ID: {user_id})\n\n📝 Problem:\n{description}\n\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    try:
                        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
                        print(f"✅ Sent issue to admin: {ADMIN_ID}")
                    except Exception as e:
                        print(f"❌ Failed to send to admin: {e}")
                        logger.error(f"Failed to send to admin: {e}")
                
                await update.message.reply_text(TEXTS[lang]['issue_submitted'], reply_markup=get_main_menu_keyboard(lang))
            else:
                await update.message.reply_text(TEXTS[lang]['issue_error'], reply_markup=get_main_menu_keyboard(lang))
        except Exception as e:
            logger.error(f"Issue save error: {e}")
            await update.message.reply_text(TEXTS[lang]['issue_error'], reply_markup=get_main_menu_keyboard(lang))
        
        context.user_data['state'] = None
    
    elif state == 'waiting_hospital_input':
        city_name = text
        await update.message.reply_text(TEXTS[lang]['searching'], reply_markup=ReplyKeyboardRemove())
        
        lat, lon, bbox, area_name = get_city_info(city_name)
        
        if not lat or not lon:
            lat, lon = 22.246, 72.688
            bbox = (22.1, 72.5, 22.4, 72.9)
            area_name = "Anklav Area"
        
        hospitals, area_name = search_hospitals_overpass(lat, lon, bbox, area_name)
        
        if hospitals:
            response = format_hospital_results(hospitals, area_name, lang)
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=get_hospital_results_keyboard(lang))
        else:
            await update.message.reply_text(TEXTS[lang]['no_hospitals'], reply_markup=get_main_menu_keyboard(lang))
        
        context.user_data['state'] = None
    
    else:
        await update.message.reply_text(TEXTS[lang]['unknown'], reply_markup=get_main_menu_keyboard(lang))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads for X-ray requests"""
    state = context.user_data.get('state')
    lang = context.user_data.get('language', 'en')
    
    if state == 'waiting_xray_image':
        # Step 5: Get X-ray image, then show doctor list
        try:
            # Download photo
            photo = update.message.photo[-1]  # Highest quality
            file = await context.bot.get_file(photo.file_id)
            
            # Save to shared location that both bots can access
            import os
            os.makedirs('xray_images', exist_ok=True)
            image_filename = f"xray_{update.effective_user.id}_{photo.file_id[-10:]}.jpg"
            image_path = os.path.join('xray_images', image_filename)
            await file.download_to_drive(image_path)
            
            # Store BOTH file_id (for patient bot) and local path (for doctor bot)
            context.user_data['patient_form']['image_path'] = image_path
            context.user_data['patient_form']['image_file_id'] = photo.file_id
            
            form = context.user_data['patient_form']
            
            await update.message.reply_text("✅ X-ray image received!\n\n⏳ Processing...")
            
            # Get available doctors from Supabase
            if supabase and supabase_connected:
                doctors_response = supabase.table('doctors').select('phone, name, phc, rating').eq('active', True).order('rating', desc=True).limit(5).execute()
                
                if doctors_response.data and len(doctors_response.data) > 0:
                    keyboard = []
                    for doc in doctors_response.data:
                        rating_stars = '⭐' * int(doc.get('rating', 0))
                        btn_text = f"Dr. {doc['name']} {rating_stars} ({doc.get('phc', 'PHC')})"
                        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"xray_doctor_{doc['phone']}")])
                    keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data="back_menu")])
                    
                    await update.message.reply_text(
                        f"✅ **Patient Details:**\n\n"
                        f"👤 {form['name']} ({form['age']}y)\n"
                        f"📍 {form['village']}\n"
                        f"🩺 {form['symptoms']}\n"
                        f"📸 X-ray image attached\n\n"
                        f"👨‍⚕️ Choose PHC doctor:",
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='Markdown'
                    )
                    context.user_data['state'] = None
                else:
                    await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
                    context.user_data['state'] = None
            else:
                await update.message.reply_text(TEXTS[lang]['error'], reply_markup=get_main_menu_keyboard(lang))
                context.user_data['state'] = None
                
        except Exception as e:
            logger.error(f"Error handling X-ray image: {e}")
            await update.message.reply_text(
                "❌ Error processing image. Please try again.",
                reply_markup=get_main_menu_keyboard(lang)
            )
            context.user_data['state'] = None
    else:
        # Photo sent but not in X-ray flow
        await update.message.reply_text(
            "❓ Please use the menu to start X-ray check first.",
            reply_markup=get_main_menu_keyboard(lang)
        )

def main() -> None:
    token = os.getenv('BOT_TOKEN')
    if not token:
        print("❌ Error: BOT_TOKEN not found in .env file")
        return
    
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start reminder scheduler in background thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    async def check_reminders():
        """Check and send medicine reminders"""
        if not supabase or not supabase_connected:
            return
        
        try:
            current_time = datetime.now().strftime('%H:%M')
            current_hour = datetime.now().strftime('%I:00 %p')
            
            response = supabase.table('reminders').select('*').eq('active', True).execute()
            reminders = response.data
            
            for reminder in reminders:
                reminder_time = reminder['time'].strip()
                
                # Check if current time matches (with some flexibility)
                if current_time in reminder_time or current_hour in reminder_time:
                    user_id = reminder['user_id']
                    medicine = reminder['medicine_name']
                    dosage = reminder['dosage']
                    
                    message = f"💊 MEDICINE REMINDER!\n\n{medicine}\n📋 {dosage}\n\n⏰ Time to take your medicine!"
                    
                    try:
                        await application.bot.send_message(chat_id=user_id, text=message)
                        print(f"✅ Sent reminder to user {user_id}: {medicine}")
                    except Exception as e:
                        logger.error(f"Failed to send reminder to {user_id}: {e}")
        
        except Exception as e:
            logger.error(f"Reminder check error: {e}")
    
    async def check_appointments():
        """Check and send appointment reminders 1 day before"""
        if not supabase or not supabase_connected:
            return
        
        try:
            from datetime import datetime, timedelta
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y')
            
            response = supabase.table('appointments').select('*').eq('reminder_sent', False).execute()
            appointments = response.data
            
            for appointment in appointments:
                if appointment['date'] == tomorrow:
                    user_id = appointment['user_id']
                    hospital = appointment['hospital']
                    time = appointment['time']
                    notes = appointment['notes']
                    
                    message = f"🔔 APPOINTMENT REMINDER!\n\nTomorrow at {time}\n🏥 {hospital}\n📝 {notes}\n\nDon't forget!"
                    
                    try:
                        await application.bot.send_message(chat_id=user_id, text=message)
                        supabase.table('appointments').update({'reminder_sent': True}).eq('id', appointment['id']).execute()
                        print(f"✅ Sent appointment reminder to user {user_id}")
                    except Exception as e:
                        logger.error(f"Failed to send appointment reminder to {user_id}: {e}")
        
        except Exception as e:
            logger.error(f"Appointment check error: {e}")
    
    # Schedule reminder checks every hour
    schedule.every().hour.do(lambda: application.create_task(check_reminders()))
    schedule.every().hour.do(lambda: application.create_task(check_appointments()))
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("✅ MediMind Rural bot is running...")
    print("🔔 Medicine reminder scheduler started")
    print("Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
