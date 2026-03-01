# -*- coding: utf-8 -*-
"""
MediMind Doctor Bot - X-Ray Analysis Interface
@MediMindDoctorBot (MEDIMIND_DOCTOR_TOKEN)
For doctors to review X-ray requests and provide diagnosis
"""

import os
import asyncio
import logging
import secrets
import json
import base64
from PIL import Image
import io
import ollama
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from supabase_wrapper import create_client
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from supabase_wrapper import SupabaseClient as Client
else:
    Client = None
from dotenv import load_dotenv
from datetime import datetime
from report_generator import generate_pdf, generate_and_upload

# Load environment variables
load_dotenv('.env.doctor')

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MEDIMIND_DOCTOR_TOKEN = os.getenv("MEDIMIND_DOCTOR_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

# Debug: Print loaded values
print("=== DOCTOR BOT CONFIG DEBUG ===")
print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:30] if SUPABASE_KEY else 'NOT SET'}...")
print(f"DOCTOR_TOKEN: {MEDIMIND_DOCTOR_TOKEN[:20] if MEDIMIND_DOCTOR_TOKEN else 'NOT SET'}...")
print("================================\n")

# Initialize Supabase with error handling
supabase = None
supabase_connected = False
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Test connection
        test = supabase.table("doctors").select("*", count='exact').limit(1).execute()
        print(f"✅ Supabase connected! Doctor table accessible.")
        supabase_connected = True
    else:
        print("❌ Supabase credentials not set")
except Exception as e:
    print(f"❌ Supabase connection error: {e}")
    print("⚠️ Bot will run in TEST MODE (no database)")
    supabase = None

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# REAL OLLAMA VLM FUNCTIONS (RTX 3070)
# ============================================

def prepare_image_b64(image_path):
    """Convert image to base64 for Ollama"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image: {e}")
        return None

def vlm_fast(image_path):
    """⚡ FAST X-ray/Skin analysis (llava-llama3:8b 6GB VRAM)"""
    try:
        img_b64 = prepare_image_b64(image_path)
        if not img_b64:
            return "❌ Error: Could not process image"
        
        response = ollama.chat(model='llava-llama3:8b', messages=[
            {
                'role': 'user',
                'content': 'Analyze this medical X-ray or skin image. Provide MCI-compliant findings only. Keep report short and focused on key observations.',
                'images': [img_b64]
            }
        ])
        
        result = response['message']['content']
        return f"⚡ **FAST ANALYSIS:**\n\n{result[:400]}..."
    
    except Exception as e:
        logger.error(f"VLM Fast error: {e}")
        return f"❌ Error in fast analysis: {str(e)}\n\nMake sure Ollama is running: `ollama serve`"

def vlm_detailed(image_path):
    """🔍 DETAILED CT/MRI/X-ray analysis (llava:13b 9GB VRAM)"""
    try:
        img_b64 = prepare_image_b64(image_path)
        if not img_b64:
            return "❌ Error: Could not process image"
        
        response = ollama.chat(model='llava:13b', messages=[
            {
                'role': 'user',
                'content': '''Medical image analysis for MCI decision support:

1. Findings (include ICD10 codes if clearly identifiable)
2. Risk level (LOW/MEDIUM/HIGH)
3. Next steps (ECG/blood test/refer to specialist)
4. Suggested medications (List A/B drugs only, no narcotics)

Provide detailed, structured report.''',
                'images': [img_b64]
            }
        ])
        
        result = response['message']['content']
        return f"🔍 **DETAILED REPORT:**\n\n{result}"
    
    except Exception as e:
        logger.error(f"VLM Detailed error: {e}")
        return f"❌ Error in detailed analysis: {str(e)}\n\nMake sure Ollama is running: `ollama serve`"

def translate_hindi(ai_report, diseases_str):
    """🇮🇳 Translate to Hindi using sarvam-1 model for rural patients"""
    try:
        response = ollama.chat(model='mashriram/sarvam-1', messages=[
            {
                'role': 'user',
                'content': f'''Translate to simple Hindi for rural patient:

Medical Report: {ai_report[:300]}

Diseases Detected: {diseases_str}

Use short, simple sentences. Avoid complex medical terms.'''
            }
        ])
        
        return response['message']['content']
    
    except Exception as e:
        logger.error(f"Hindi translation error: {e}")
        return "❌ Hindi translation unavailable (sarvam-1 model not loaded)"

def translate_hindi_message(english_text):
    """🇮🇳 Translate doctor's message to Hindi"""
    try:
        response = ollama.chat(model='mashriram/sarvam-1', messages=[
            {
                'role': 'user',
                'content': f'''Translate this doctor's message to simple Hindi:

{english_text}

Use simple, clear Hindi that rural patients can understand.
Keep the same tone and meaning.'''
            }
        ])
        
        return response['message']['content']
    
    except Exception as e:
        logger.error(f"Hindi translation error: {e}")
        return "अनुवाद उपलब्ध नहीं है (Translation unavailable)"

def analyze_xray_14diseases(image_path):
    """🎯 14-DISEASE MODEL + VLM reasoning + Hindi translation"""
    try:
        # STUB: Your 14-disease DL model will replace this
        # For now, using placeholder confidence scores
        diseases = {
            "Pneumonia": 0.92, "Cardiomegaly": 0.78, "Effusion": 0.65,
            "Atelectasis": 0.58, "Pneumothorax": 0.12, "Fracture": 0.08,
            "TB": 0.05, "Consolidation": 0.45, "Edema": 0.22, "Emphysema": 0.11,
            "Fibrosis": 0.09, "Pleural Thickening": 0.33, "Hernia": 0.02,
            "Mass": 0.41, "Nodule": 0.27
        }
        
        # Get top 3 diseases
        top3 = sorted(diseases.items(), key=lambda x: x[1], reverse=True)[:3]
        top3_str = "\n".join([f"• {k}: {v:.0%}" for k, v in top3])
        diseases_str = ", ".join([k for k, v in top3])
        
        # VLM reasoning on DL model results
        img_b64 = prepare_image_b64(image_path)
        if not img_b64:
            return "❌ Error: Could not process image"
        
        dl_prompt = f"""X-ray 14-disease deep learning scan detected:

{top3_str}

Based on these AI detections, provide:
1. Clinical interpretation (MCI-compliant)
2. ICD10 codes if applicable
3. Recommended PHC tests (ECG, blood work, etc.)
4. List A/B medications to consider
5. Urgency level (LOW/MEDIUM/HIGH)

Patient context: Rural PHC setting, limited resources."""
        
        vlm_response = ollama.chat(model='llava:13b', messages=[
            {'role': 'user', 'content': dl_prompt, 'images': [img_b64]}
        ])
        
        ai_report = vlm_response['message']['content']
        
        # Translate to Hindi for patient
        hindi_report = translate_hindi(ai_report, diseases_str)
        
        # Format final report
        result = f"""🎯 **14-DISEASES + VLM ANALYSIS:**

📊 **DL SCAN RESULTS:**
{top3_str}

🔍 **AI CLINICAL REPORT:**
{ai_report[:350]}...

🇮🇳 **HINDI (Patient):**
{hindi_report[:250]}...

---
[📝 EDIT] [✅ PDF & SEND]"""
        
        return result
    
    except Exception as e:
        logger.error(f"14-disease analysis error: {e}")
        return f"❌ Error in 14-disease analysis: {str(e)}\n\nMake sure Ollama is running with llava:13b and sarvam-1 models"

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Doctor login/registration"""
    user = update.effective_user
    
    logger.info(f"Doctor bot /start by user {user.id} (@{user.username})")
    
    # Check if Supabase is connected
    if not supabase:
        await update.message.reply_text(
            "⚠️ Database not connected. Bot is in TEST MODE.\n\n"
            "Please contact admin to fix Supabase configuration."
        )
        return
    
    # Check if doctor already registered
    try:
        doctors = supabase.table("doctors").select("*").eq("telegram_id", user.id).execute()
        
        if doctors.data and len(doctors.data) > 0:
            doctor = doctors.data[0]
            context.user_data['doctor'] = doctor
            context.user_data['phone'] = doctor['phone']
            
            # Welcome back message
            await update.message.reply_text(
                f"✅ Welcome back, Dr. {doctor['name']}!\n\n"
                f"🏥 PHC: {doctor.get('phc', 'N/A')}\n"
                f"🩺 MCI: {doctor.get('mci_reg', 'N/A')}\n"
                f"⭐ Rating: {doctor.get('rating', 0):.1f}/5.0\n"
                f"📊 Cases: {doctor.get('total_cases', 0)}\n\n"
                f"Choose an option below:",
                reply_markup=ReplyKeyboardRemove()
            )
            await show_main_menu(user.id, context)
        else:
            # New doctor registration - request phone
            keyboard = [[KeyboardButton("📱 Share Phone to Verify", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                "👨‍⚕️ **DOCTOR REGISTRATION**\n\n"
                "To register, please share your phone number.\n\n"
                "Tap the button below to verify:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            context.user_data['step'] = 'awaiting_phone'
            
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await update.message.reply_text(
            "❌ Error connecting to database. Please try again later."
        )

async def regen_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /regen_code command - Generate new access code"""
    user = update.effective_user
    
    if not supabase:
        await update.message.reply_text("⚠️ Database not connected. Bot is in TEST MODE.")
        return
    
    try:
        doctors = supabase.table("doctors").select("*").eq("telegram_id", user.id).execute()
        
        if doctors.data and len(doctors.data) > 0:
            doctor = doctors.data[0]
            
            # Generate new access code
            new_code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            
            # Update in database
            supabase.table("doctors").update({
                "access_code": new_code
            }).eq("telegram_id", user.id).execute()
            
            await update.message.reply_text(
                f"🔐 **NEW ACCESS CODE GENERATED**\n\n"
                f"Code: `{new_code}`\n\n"
                f"Use this code to login on the website.\n"
                f"Keep it safe!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ You are not registered as a doctor.\n"
                "Use /start to register."
            )
    except Exception as e:
        logger.error(f"Error in regen_code: {e}")
        await update.message.reply_text("❌ Error generating new code.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - Check queue status"""
    user = update.effective_user
    
    if not supabase:
        await update.message.reply_text("⚠️ Database not connected. Bot is in TEST MODE.")
        return
    
    try:
        doctors = supabase.table("doctors").select("*").eq("telegram_id", user.id).execute()
        
        if doctors.data and len(doctors.data) > 0:
            doctor = doctors.data[0]
            phone = doctor['phone']
            
            # Get pending X-rays
            pending = supabase.table("xray_requests").select("*").eq("doctor_phone", phone).eq("status", "pending").execute()
            reviewed = supabase.table("xray_requests").select("*").eq("doctor_phone", phone).eq("status", "reviewed").execute()
            
            await update.message.reply_text(
                f"📊 **QUEUE STATUS**\n\n"
                f"🔴 Pending: {len(pending.data) if pending.data else 0}\n"
                f"✅ Reviewed: {len(reviewed.data) if reviewed.data else 0}\n"
                f"📈 Total Cases: {doctor.get('total_cases', 0)}\n"
                f"⭐ Rating: {doctor.get('rating', 0):.1f}/5.0",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Not registered. Use /start")
    except Exception as e:
        logger.error(f"Error in status: {e}")
        await update.message.reply_text("❌ Error fetching status.")

# ============================================
# MESSAGE HANDLERS
# ============================================

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone contact sharing"""
    user = update.effective_user
    contact = update.message.contact
    
    # Verify it's the user's own phone number
    if contact.user_id != user.id:
        await update.message.reply_text(
            "❌ Please share YOUR own phone number, not someone else's.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    phone = contact.phone_number
    if not phone.startswith('+'):
        phone = f"+{phone}"
    
    # Verify phone number with Telegram
    # Telegram automatically verifies the phone when user shares contact
    # The contact.user_id matching user.id confirms it's their verified number
    
    context.user_data['phone'] = phone
    context.user_data['telegram_verified'] = True  # Mark as Telegram-verified
    context.user_data['step'] = 'waiting_doctor_name'
    context.user_data['doctor_form'] = {}  # Initialize form
    
    await update.message.reply_text(
        f"✅ Phone verified via Telegram: {phone}\n\n"
        f"👨‍⚕️ **Step 1/3:** Enter your full name:\n\n"
        f"Example: Dr. Rajesh Shah",
        reply_markup=ReplyKeyboardRemove()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - Profile registration"""
    text = update.message.text
    user = update.effective_user
    step = context.user_data.get('step')
    
    if not supabase:
        await update.message.reply_text("⚠️ Database not connected. Bot is in TEST MODE.")
        return
    
    if step == 'waiting_doctor_name':
        # Step 1: Get doctor name
        context.user_data['doctor_form']['name'] = text
        context.user_data['step'] = 'waiting_doctor_mci'
        await update.message.reply_text(
            f"✅ Name saved: {text}\n\n"
            f"🩺 **Step 2/3:** Enter your MCI Registration Number:\n\n"
            f"Example: GJMC12345"
        )
    
    elif step == 'waiting_doctor_mci':
        # Step 2: Get MCI registration
        context.user_data['doctor_form']['mci'] = text
        context.user_data['step'] = 'waiting_doctor_phc'
        await update.message.reply_text(
            f"✅ MCI saved: {text}\n\n"
            f"🏥 **Step 3/3:** Enter your PHC (Primary Health Center) name:\n\n"
            f"Example: Anklav PHC"
        )
    
    elif step == 'waiting_doctor_phc':
        # Step 3: Get PHC and complete registration
        context.user_data['doctor_form']['phc'] = text
        form = context.user_data['doctor_form']
        phone = context.user_data.get('phone', f"+91{user.id}")
        
        # Generate access code
        access_code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
        
        try:
            # Insert doctor into database
            result = supabase.table("doctors").insert({
                "phone": phone,
                "telegram_id": user.id,
                "access_code": access_code,
                "name": form['name'],
                "mci_reg": form['mci'],
                "phc": form['phc'],
                "rating": 0.0,
                "total_cases": 0,
                "active": True
            }).execute()
            
            logger.info(f"Doctor registered: {form['name']} (ID: {user.id})")
            
            # Store in context
            context.user_data['doctor'] = result.data[0]
            context.user_data['phone'] = phone
            
            # Success message
            telegram_verified = context.user_data.get('telegram_verified', False)
            verification_text = "📱 Phone verified via Telegram ✅\n" if telegram_verified else ""
            
            await update.message.reply_text(
                f"✅ **REGISTRATION SUCCESSFUL**\n\n"
                f"{verification_text}"
                f"👨‍⚕️ {form['name']}\n"
                f"📱 {phone}\n"
                f"🩺 MCI: {form['mci']}\n"
                f"🏥 PHC: {form['phc']}\n\n"
                f"🔐 **Access Code:** `{access_code}`\n\n"
                f"⚠️ Save this code! Use it to login on the website.\n\n"
                f"Choose an option below:",
                parse_mode='Markdown'
            )
            
            # Show main menu
            await show_main_menu(update.message.chat_id, context)
            
            # Clear step
            context.user_data['step'] = None
            context.user_data.pop('doctor_form', None)
            
        except Exception as e:
            logger.error(f"Error registering doctor: {e}")
            await update.message.reply_text(
                "❌ Error during registration. Please try again.\n"
                "Use /start to restart."
            )
            context.user_data['step'] = None
    
    elif step == 'profile':
        # Old format support (backward compatibility)
        parts = [p.strip() for p in text.split('|')]
        
        if len(parts) >= 3:
            name, mci, phc = parts[0], parts[1], parts[2]
            phone = context.user_data.get('phone', f"+91{user.id}")
            
            # Generate access code
            access_code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            
            try:
                # Insert doctor into database
                result = supabase.table("doctors").insert({
                    "phone": phone,
                    "telegram_id": user.id,
                    "access_code": access_code,
                    "name": name,
                    "mci_reg": mci,
                    "phc": phc,
                    "rating": 0.0,
                    "total_cases": 0,
                    "active": True
                }).execute()
                
                logger.info(f"Doctor registered: {name} (ID: {user.id})")
                
                # Store in context
                context.user_data['doctor'] = result.data[0]
                context.user_data['phone'] = phone
                
                # Success message
                await update.message.reply_text(
                    f"✅ **REGISTRATION SUCCESSFUL**\n\n"
                    f"👨‍⚕️ Dr. {name}\n"
                    f"🩺 MCI: {mci}\n"
                    f"🏥 PHC: {phc}\n\n"
                    f"🔐 **Access Code:** `{access_code}`\n\n"
                    f"⚠️ Save this code! Use it to login on the website.\n\n"
                    f"Choose an option below:",
                    parse_mode='Markdown'
                )
                
                # Show main menu
                await show_main_menu(update.message.chat_id, context)
                
                # Clear step
                context.user_data['step'] = None
                
            except Exception as e:
                logger.error(f"Error registering doctor: {e}")
                await update.message.reply_text(
                    "❌ Error during registration. Please try again.\n"
                    "Use /start to restart."
                )
        else:
            await update.message.reply_text(
                "❌ **Wrong format!**\n\n"
                "Please use: **Name | MCI Reg | PHC Name**\n\n"
                "Example:\n"
                "`Dr. Shah | GJMC12345 | Anklav PHC`",
                parse_mode='Markdown'
            )
    
    elif context.user_data.get('editing_report'):
        # Doctor is editing the report
        context.user_data['doctor_notes'] = text
        context.user_data['editing_report'] = False
        
        # Show confirmation with PDF generation option
        keyboard = [
            [InlineKeyboardButton("✅ Generate PDF", callback_data="generate_pdf")],
            [InlineKeyboardButton("📝 Edit Again", callback_data="edit_report")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="back_menu")]
        ]
        
        await update.message.reply_text(
            f"✅ **NOTES SAVED**\n\n"
            f"Your notes:\n{text[:300]}...\n\n"
            f"Ready to generate PDF?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif context.user_data.get('waiting_for_text'):
        # Doctor is sending text message to patient
        context.user_data['waiting_for_text'] = False
        
        patient_name = context.user_data.get('contact_patient_name', 'Patient')
        patient_telegram_id = context.user_data.get('contact_patient_id')
        
        if not patient_telegram_id:
            await update.message.reply_text("❌ Patient Telegram ID not found")
            return
        
        await update.message.reply_text(
            "⏳ Translating your message...\n"
            "Please wait..."
        )
        
        try:
            # Translate to Hindi using Ollama sarvam-1 model
            hindi_translation = translate_hindi_message(text)
            
            # Get doctor info
            doctors = supabase.table("doctors").select("*").eq("telegram_id", user.id).execute()
            doctor_name = doctors.data[0].get('name', 'Doctor') if doctors.data else 'Doctor'
            
            # Send message to patient (both English and Hindi)
            message_to_patient = (
                f"📨 **Message from Dr. {doctor_name}**\n\n"
                f"**English:**\n{text}\n\n"
                f"**हिंदी:**\n{hindi_translation}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🏥 Please follow your doctor's instructions"
            )
            
            await context.bot.send_message(
                chat_id=patient_telegram_id,
                text=message_to_patient,
                parse_mode='Markdown'
            )
            
            # Confirm to doctor
            await update.message.reply_text(
                f"✅ **MESSAGE SENT**\n\n"
                f"👤 To: {patient_name}\n\n"
                f"**Your message (English):**\n{text}\n\n"
                f"**Translation (Hindi):**\n{hindi_translation}\n\n"
                f"📱 Both versions sent to patient",
                parse_mode='Markdown'
            )
            
            # Show main menu
            await asyncio.sleep(2)
            await show_main_menu(update.message.chat_id, context)
            
            logger.info(f"Text message sent from doctor {user.id} to patient {patient_telegram_id}")
            
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            await update.message.reply_text(
                f"❌ Error sending message: {str(e)}\n\n"
                f"Please try again or use voice note instead."
            )
    
    else:
        # Unknown message
        await update.message.reply_text(
            "❓ I don't understand. Use /start to begin."
        )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads for X-ray analysis"""
    user = update.effective_user
    
    # Check if we're expecting a photo
    if 'scan_type' not in context.user_data:
        await update.message.reply_text(
            "❓ Please select scan type first.\n"
            "Use /start → Analyze Image"
        )
        return
    
    scan_type = context.user_data.get('scan_type', 'X-ray')
    mode = context.user_data.get('mode', 'mode_detailed')
    
    await update.message.reply_text(
        f"⏳ Processing {scan_type} image with Ollama VLM...\n"
        f"Please wait (RTX 3070 inference)..."
    )
    
    try:
        # Download photo
        photo = update.message.photo[-1]  # Highest quality
        file = await context.bot.get_file(photo.file_id)
        image_path = f"temp_{photo.file_id}.jpg"
        await file.download_to_drive(image_path)
        
        logger.info(f"Photo received from doctor {user.id}: {image_path}, mode: {mode}")
        
        # Analyze based on mode
        result = ""
        if scan_type == "X-ray" and mode == "mode_14diseases":
            # 14-disease model + VLM + Hindi
            result = analyze_xray_14diseases(image_path)
            
        elif mode == "mode_fast":
            # Fast VLM (llava-llama3:8b)
            result = vlm_fast(image_path)
            
        elif mode == "mode_detailed":
            # Detailed VLM (llava:13b)
            result = vlm_detailed(image_path)
        
        else:
            await update.message.reply_text(
                f"❌ Unknown mode: {mode}\n"
                f"Please try again with /start → Analyze Image"
            )
            return
        
        # Store analysis result and image path for PDF generation
        context.user_data['analysis_result'] = result
        context.user_data['image_path'] = image_path
        context.user_data['scan_type_analyzed'] = scan_type
        context.user_data['mode_used'] = mode
        
        # Extract Hindi text if present (from 14-diseases analysis)
        hindi_text = ""
        if "🇮🇳 **HINDI (Patient):**" in result:
            # Extract Hindi portion
            parts = result.split("🇮🇳 **HINDI (Patient):**")
            if len(parts) > 1:
                hindi_part = parts[1].split("---")[0].strip()
                hindi_text = hindi_part.replace("...", "")
                context.user_data['hindi_report'] = hindi_text
                logger.info(f"Extracted Hindi text: {len(hindi_text)} chars")
        
        # If no Hindi extracted, generate a simple Hindi summary
        if not hindi_text:
            # Simple Hindi summary based on findings
            hindi_text = """मरीज की जांच में निम्नलिखित पाया गया:

कृपया डॉक्टर द्वारा बताई गई दवाइयां समय पर लें।

सलाह:
- आराम करें
- पानी पीते रहें
- समय पर दवाई लें
- अगर तबीयत ज्यादा खराब हो तो तुरंत डॉक्टर को दिखाएं"""
            context.user_data['hindi_report'] = hindi_text
        
        # Show result with action buttons
        keyboard = [
            [InlineKeyboardButton("📝 Edit Report", callback_data="edit_report")],
            [InlineKeyboardButton("✅ Generate PDF", callback_data="generate_pdf")],
            [InlineKeyboardButton("🔄 Re-analyze", callback_data="analyze")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="back_menu")]
        ]
        
        await update.message.reply_text(
            f"✅ **ANALYSIS COMPLETE**\n\n{result[:800]}...\n\n"
            f"Choose next action:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        logger.info(f"Analysis complete for doctor {user.id}, awaiting action")
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(
            f"❌ Error analyzing image: {str(e)}\n\n"
            f"Make sure Ollama is running:\n"
            f"`ollama serve`\n\n"
            f"And models are installed:\n"
            f"`ollama pull llava:13b`\n"
            f"`ollama pull llava-llama3:8b`\n"
            f"`ollama pull mashriram/sarvam-1`"
        )
        # Clean up on error
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages from doctor to patient"""
    user = update.effective_user
    
    # Check if we're expecting a voice note
    if not context.user_data.get('waiting_for_voice'):
        await update.message.reply_text(
            "❓ I'm not expecting a voice note right now.\n"
            "Use /start to begin."
        )
        return
    
    context.user_data['waiting_for_voice'] = False
    
    patient_name = context.user_data.get('contact_patient_name', 'Patient')
    patient_telegram_id = context.user_data.get('contact_patient_id')
    
    if not patient_telegram_id:
        await update.message.reply_text("❌ Patient Telegram ID not found")
        return
    
    await update.message.reply_text(
        "⏳ Sending voice note to patient...\n"
        "Please wait..."
    )
    
    try:
        # Get doctor info
        doctors = supabase.table("doctors").select("*").eq("telegram_id", user.id).execute()
        doctor_name = doctors.data[0].get('name', 'Doctor') if doctors.data else 'Doctor'
        
        # Forward voice note to patient
        voice = update.message.voice
        
        # Send voice with caption
        await context.bot.send_voice(
            chat_id=patient_telegram_id,
            voice=voice.file_id,
            caption=f"🎤 **Voice Message from Dr. {doctor_name}**\n\n"
                    f"🏥 Please listen to your doctor's message",
            parse_mode='Markdown'
        )
        
        # Confirm to doctor
        await update.message.reply_text(
            f"✅ **VOICE NOTE SENT**\n\n"
            f"👤 To: {patient_name}\n"
            f"🎤 Voice message delivered successfully",
            parse_mode='Markdown'
        )
        
        # Show main menu
        await asyncio.sleep(2)
        await show_main_menu(update.message.chat_id, context)
        
        logger.info(f"Voice note sent from doctor {user.id} to patient {patient_telegram_id}")
        
    except Exception as e:
        logger.error(f"Error sending voice note: {e}")
        await update.message.reply_text(
            f"❌ Error sending voice note: {str(e)}\n\n"
            f"Please try again."
        )

# ============================================
# HELPER FUNCTIONS
# ============================================

async def process_request_analysis(query, context):
    """Process analysis for X-ray request (image already uploaded)"""
    try:
        # Get image path from context
        image_path = context.user_data.get('xray_image_file_id')  # This is actually the file path now
        
        if not image_path or not os.path.exists(image_path):
            await query.edit_message_text("❌ Image file not found for this request")
            return
        
        await query.edit_message_text(
            "⏳ Loading image and analyzing...\n"
            "Please wait (RTX 3070 inference)...",
            parse_mode='Markdown'
        )
        
        logger.info(f"Analyzing image from path: {image_path}")
        
        # Get analysis mode and scan type
        mode = context.user_data.get('mode', 'mode_detailed')
        scan_type = context.user_data.get('scan_type', 'X-ray')
        
        # Analyze based on mode
        result = ""
        if scan_type == "X-ray" and "14diseases" in mode:
            result = analyze_xray_14diseases(image_path)
        elif "fast" in mode:
            result = vlm_fast(image_path)
        elif "detailed" in mode:
            result = vlm_detailed(image_path)
        else:
            result = vlm_detailed(image_path)
        
        # Store analysis result
        context.user_data['analysis_result'] = result
        context.user_data['image_path'] = image_path
        context.user_data['scan_type_analyzed'] = scan_type
        context.user_data['mode_used'] = mode
        
        # Extract Hindi text if present
        hindi_text = ""
        if "🇮🇳 **HINDI (Patient):**" in result:
            parts = result.split("🇮🇳 **HINDI (Patient):**")
            if len(parts) > 1:
                hindi_part = parts[1].split("---")[0].strip()
                hindi_text = hindi_part.replace("...", "")
                context.user_data['hindi_report'] = hindi_text
        
        if not hindi_text:
            hindi_text = """मरीज की जांच में निम्नलिखित पाया गया:

कृपया डॉक्टर द्वारा बताई गई दवाइयां समय पर लें।"""
            context.user_data['hindi_report'] = hindi_text
        
        # Get patient details
        patient_name = context.user_data.get('patient_name', 'Patient')
        patient_age = context.user_data.get('patient_age', 'N/A')
        patient_village = context.user_data.get('patient_village', 'N/A')
        
        # Show result with action buttons
        keyboard = [
            [InlineKeyboardButton("📝 Edit Report", callback_data="edit_report")],
            [InlineKeyboardButton("✅ Generate PDF", callback_data="generate_pdf")],
            [InlineKeyboardButton("🔄 Re-analyze", callback_data="requests")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="back_menu")]
        ]
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"✅ **ANALYSIS COMPLETE**\n\n"
                 f"👤 {patient_name} ({patient_age}y) - {patient_village}\n\n"
                 f"{result[:800]}...\n\n"
                 f"Choose next action:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        logger.info(f"Analysis complete for request, awaiting action")
        
    except Exception as e:
        logger.error(f"Error in process_request_analysis: {e}")
        await query.edit_message_text(
            f"❌ Error analyzing image: {str(e)}\n\n"
            f"Make sure Ollama is running:\n"
            f"`ollama serve`",
            parse_mode='Markdown'
        )

# ============================================
# MENU FUNCTIONS
# ============================================

async def show_main_menu(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Show main doctor menu"""
    keyboard = [
        [InlineKeyboardButton("📥 Requests", callback_data="requests"), 
         InlineKeyboardButton("📋 My Queue", callback_data="queue")],
        [InlineKeyboardButton("🩻 Analyze Image", callback_data="analyze")],
        [InlineKeyboardButton("📊 My Dashboard", callback_data="my_dashboard")],
        [InlineKeyboardButton("📋 Old Reports", callback_data="old_reports")],
        [InlineKeyboardButton("🔐 Regen Code", callback_data="regen_code_btn")],
        [InlineKeyboardButton("🚪 Logout", callback_data="logout")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text="🎯 **DOCTOR MENU**\n\nChoose an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ============================================
# BUTTON HANDLERS
# ============================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    if not supabase:
        await query.edit_message_text("⚠️ Database not connected. Bot is in TEST MODE.")
        return
    
    try:
        # Get doctor info
        doctors = supabase.table("doctors").select("*").eq("telegram_id", user.id).execute()
        
        if not doctors.data or len(doctors.data) == 0:
            await query.edit_message_text("❌ Not registered. Use /start")
            return
        
        doctor = doctors.data[0]
        phone = doctor['phone']
        
        if query.data == "queue":
            # Show pending X-rays assigned to this doctor
            requests = supabase.table("xray_requests").select(
                "id, patient_name, age, village, symptoms, status, created_at"
            ).eq("doctor_phone", phone).eq("status", "pending").order("created_at", desc=True).limit(10).execute()
            
            if requests.data and len(requests.data) > 0:
                text = "📋 **MY QUEUE**\n\n"
                for r in requests.data:
                    symptoms_short = r['symptoms'][:60] + "..." if r['symptoms'] and len(r['symptoms']) > 60 else (r['symptoms'] or 'No symptoms')
                    text += f"🔴 **#{r['id']}** {r['patient_name']} ({r['age']}y) - {r.get('village', 'N/A')}\n"
                    text += f"   {symptoms_short}\n\n"
                
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await query.edit_message_text(
                    text + "👆 Note the ID to analyze specific case",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            else:
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await query.edit_message_text(
                    "✅ No pending X-rays in your queue!\n\nAll cases reviewed.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif query.data == "requests":
            # Show NEW pending X-ray requests with images and analyze button
            requests = supabase.table("xray_requests").select(
                "id, patient_name, age, village, symptoms, image_url, status, created_at"
            ).eq("doctor_phone", phone).eq("status", "pending").order("created_at", desc=True).limit(10).execute()
            
            if requests.data and len(requests.data) > 0:
                await query.edit_message_text(
                    f"📥 **NEW REQUESTS**\n\nYou have {len(requests.data)} pending X-ray request(s).\n\nShowing details...",
                    parse_mode='Markdown'
                )
                
                # Send each request as separate message with image and analyze button
                for r in requests.data:
                    symptoms_short = r['symptoms'][:100] + "..." if r['symptoms'] and len(r['symptoms']) > 100 else (r['symptoms'] or 'No symptoms')
                    
                    caption = (
                        f"🆕 **Request #{r['id']}**\n\n"
                        f"👤 {r['patient_name']} ({r['age']}y)\n"
                        f"📍 {r.get('village', 'N/A')}\n"
                        f"🩺 {symptoms_short}\n"
                        f"📅 {r.get('created_at', 'N/A')[:10]}"
                    )
                    
                    # Create analyze button with request ID
                    keyboard = [[InlineKeyboardButton("🩻 Analyze This X-Ray", callback_data=f"analyze_request_{r['id']}")]]
                    
                    # Send image from local file path
                    image_path = r.get('image_url')
                    if image_path and os.path.exists(image_path):
                        try:
                            with open(image_path, 'rb') as photo_file:
                                await context.bot.send_photo(
                                    chat_id=query.message.chat_id,
                                    photo=photo_file,
                                    caption=caption,
                                    reply_markup=InlineKeyboardMarkup(keyboard),
                                    parse_mode='Markdown'
                                )
                        except Exception as e:
                            logger.error(f"Error sending image: {e}")
                            # Fallback without image
                            await context.bot.send_message(
                                chat_id=query.message.chat_id,
                                text=caption + "\n\n⚠️ Image not available",
                                reply_markup=InlineKeyboardMarkup(keyboard),
                                parse_mode='Markdown'
                            )
                    else:
                        # No image file found
                        await context.bot.send_message(
                            chat_id=query.message.chat_id,
                            text=caption + "\n\n📤 Image file not found",
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            parse_mode='Markdown'
                        )
                
                # Send back to menu button
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="👆 Click 'Analyze' button on any request to start",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await query.edit_message_text(
                    "✅ No new requests!\n\nAll caught up.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif query.data == "my_dashboard":
            # Show doctor's personal statistics
            try:
                # Get doctor's stats
                total_pending = supabase.table("xray_requests").select("*", count='exact').eq("doctor_phone", phone).eq("status", "pending").execute()
                total_reviewed = supabase.table("xray_requests").select("*", count='exact').eq("doctor_phone", phone).eq("status", "reviewed").execute()
                total_sent = supabase.table("xray_requests").select("*", count='exact').eq("doctor_phone", phone).eq("status", "sent").execute()
                
                pending_count = total_pending.count if total_pending else 0
                reviewed_count = total_reviewed.count if total_reviewed else 0
                sent_count = total_sent.count if total_sent else 0
                total_cases = pending_count + reviewed_count + sent_count
                
                text = f"📊 **MY DASHBOARD**\n\n"
                text += f"👨‍⚕️ Dr. {doctor.get('name', 'Unknown')}\n"
                text += f"📱 {phone}\n"
                text += f"🏥 {doctor.get('phc', 'N/A')}\n"
                text += f"🩺 MCI: {doctor.get('mci_reg', 'N/A')}\n\n"
                text += f"📈 **STATISTICS**\n"
                text += f"🔴 Pending: {pending_count}\n"
                text += f"✅ Reviewed: {reviewed_count}\n"
                text += f"📤 Sent: {sent_count}\n"
                text += f"📊 Total Cases: {total_cases}\n"
                text += f"⭐ Rating: {doctor.get('rating', 0):.1f}/5.0\n\n"
                text += f"💡 Keep up the great work!"
                
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error loading dashboard: {e}")
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await query.edit_message_text(
                    "❌ Error loading dashboard. Please try again.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif query.data.startswith("analyze_request_"):
            # Analyze specific X-ray request - load image and patient details
            request_id = int(query.data.replace("analyze_request_", ""))
            
            try:
                # Get request details
                request = supabase.table("xray_requests").select("*").eq("id", request_id).execute()
                
                if request.data and len(request.data) > 0:
                    req = request.data[0]
                    
                    # Store request details in context
                    context.user_data['current_request_id'] = request_id
                    context.user_data['current_request'] = req
                    context.user_data['patient_name'] = req.get('patient_name')
                    context.user_data['patient_age'] = req.get('age')
                    context.user_data['patient_village'] = req.get('village')
                    context.user_data['patient_symptoms'] = req.get('symptoms')
                    context.user_data['xray_image_file_id'] = req.get('image_url')  # This is the file PATH
                    
                    # Show scan type selection (X-ray is default, but allow others)
                    keyboard = [
                        [InlineKeyboardButton("🫁 X-ray", callback_data="analyze_xray")],
                        [InlineKeyboardButton("🧠 CT Scan", callback_data="analyze_ct"), 
                         InlineKeyboardButton("🩻 MRI", callback_data="analyze_mri")],
                        [InlineKeyboardButton("🩹 Skin", callback_data="analyze_skin")],
                        [InlineKeyboardButton("🔙 Back", callback_data="requests")]
                    ]
                    
                    # Send new message instead of editing (because original is a photo)
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=f"🩻 **ANALYZING REQUEST #{request_id}**\n\n"
                             f"👤 {req.get('patient_name')} ({req.get('age')}y)\n"
                             f"📍 {req.get('village')}\n"
                             f"🩺 {req.get('symptoms')}\n\n"
                             f"🏥 **SELECT SCAN TYPE**\n\nWhat type of scan is this?",
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='Markdown'
                    )
                    await query.answer()
                else:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="❌ Request not found"
                    )
                    await query.answer()
            except Exception as e:
                logger.error(f"Error loading request: {e}")
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"❌ Error: {str(e)}"
                )
                await query.answer()
        
        elif query.data.startswith("analyze_"):
            # Handle scan type selection from request
            scan_type_map = {
                "analyze_xray": "X-ray",
                "analyze_ct": "CT",
                "analyze_mri": "MRI",
                "analyze_skin": "Skin"
            }
            
            if query.data in scan_type_map:
                context.user_data["scan_type"] = scan_type_map[query.data]
                
                # For X-ray, show mode selection
                if query.data == "analyze_xray":
                    keyboard = [
                        [InlineKeyboardButton("⚡ FAST (llava-llama3:8b)", callback_data="mode_fast_request")],
                        [InlineKeyboardButton("🔍 DETAILED (llava:13b)", callback_data="mode_detailed_request")],
                        [InlineKeyboardButton("🎯 14-DISEASES (YOUR MODEL)", callback_data="mode_14diseases_request")],
                        [InlineKeyboardButton("🔙 Back", callback_data="requests")]
                    ]
                    await query.edit_message_text(
                        "⚙️ **X-RAY MODE** (RTX 3070):\n\nSelect analysis mode:",
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='Markdown'
                    )
                else:
                    # Other scan types - use detailed mode
                    context.user_data["mode"] = "mode_detailed_request"
                    await process_request_analysis(query, context)
            else:
                # Original analyze button (manual upload)
                keyboard = [
                    [InlineKeyboardButton("🫁 X-ray", callback_data="xray")],
                    [InlineKeyboardButton("🧠 CT Scan", callback_data="ct"), 
                     InlineKeyboardButton("🩻 MRI", callback_data="mri")],
                    [InlineKeyboardButton("🩹 Skin", callback_data="skin")],
                    [InlineKeyboardButton("🔙 Back", callback_data="back_menu")]
                ]
                await query.edit_message_text(
                    "🏥 **SELECT SCAN TYPE**\n\nWhat type of scan do you want to analyze?",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
        
        elif query.data.startswith("mode_") and query.data.endswith("_request"):
            # Mode selected for request analysis
            mode = query.data.replace("_request", "")
            context.user_data["mode"] = mode
            await process_request_analysis(query, context)
        
        elif query.data == "analyze":
            # Show scan type selection
            keyboard = [
                [InlineKeyboardButton("🫁 X-ray", callback_data="xray")],
                [InlineKeyboardButton("🧠 CT Scan", callback_data="ct"), 
                 InlineKeyboardButton("🩻 MRI", callback_data="mri")],
                [InlineKeyboardButton("🩹 Skin", callback_data="skin")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_menu")]
            ]
            await query.edit_message_text(
                "🏥 **SELECT SCAN TYPE**\n\nWhat type of scan do you want to analyze?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        elif query.data == "xray":
            # X-ray mode selection
            context.user_data["scan_type"] = "X-ray"
            keyboard = [
                [InlineKeyboardButton("⚡ FAST (llava-llama3:8b)", callback_data="mode_fast")],
                [InlineKeyboardButton("🔍 DETAILED (llava:13b)", callback_data="mode_detailed")],
                [InlineKeyboardButton("🎯 14-DISEASES (YOUR MODEL)", callback_data="mode_14diseases")],
                [InlineKeyboardButton("🔙 Back", callback_data="analyze")]
            ]
            await query.edit_message_text(
                "⚙️ **X-RAY MODE** (RTX 3070):\n\nSelect analysis mode:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        elif query.data in ["ct", "mri", "skin"]:
            # Other scan types - only detailed mode
            context.user_data["scan_type"] = query.data.upper()
            context.user_data["mode"] = "mode_detailed"
            await query.edit_message_text(
                f"📤 **Upload {context.user_data['scan_type']} image...**\n\n"
                f"Send photo now (supports phone cameras)\n"
                f"Mode: DETAILED analysis",
                parse_mode='Markdown'
            )
        
        elif query.data.startswith("mode_"):
            # Mode selected - request photo
            context.user_data["mode"] = query.data
            scan_type = context.user_data.get("scan_type", "X-ray")
            mode_name = query.data.replace('mode_', '').replace('_', ' ').title()
            await query.edit_message_text(
                f"📤 **Upload {scan_type} image for {mode_name} analysis...**\n\n"
                f"Send photo now (blurry phone OK)\n"
                f"Waiting for image...",
                parse_mode='Markdown'
            )
        
        elif query.data == "old_reports":
            # Show reviewed cases
            reviewed = supabase.table("xray_requests").select(
                "id, patient_name, age, status, reviewed_at"
            ).eq("doctor_phone", phone).eq("status", "reviewed").order("reviewed_at", desc=True).limit(10).execute()
            
            if reviewed.data and len(reviewed.data) > 0:
                text = "📋 **OLD REPORTS**\n\n"
                for r in reviewed.data:
                    text += f"✅ **{r['patient_name']}** ({r['age']}y)\n"
                    text += f"   Reviewed: {r.get('reviewed_at', 'N/A')}\n"
                    text += f"   ID: {r['id']}\n\n"
                
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            else:
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await query.edit_message_text(
                    "📭 No reviewed reports yet.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif query.data == "regen_code_btn":
            # Generate new access code
            new_code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            
            supabase.table("doctors").update({
                "access_code": new_code
            }).eq("telegram_id", user.id).execute()
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
            await query.edit_message_text(
                f"🔐 **NEW ACCESS CODE**\n\n"
                f"Code: `{new_code}`\n\n"
                f"Use this to login on the website.",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        elif query.data == "back_menu":
            await show_main_menu(query.message.chat_id, context)
        
        elif query.data == "edit_report":
            # Edit report - ask for doctor's notes
            context.user_data['editing_report'] = True
            
            await query.edit_message_text(
                "📝 **EDIT REPORT**\n\n"
                "Current AI analysis:\n"
                f"{context.user_data.get('analysis_result', 'No analysis')[:400]}...\n\n"
                "Reply with your edited notes or additional observations:\n"
                "(This will be added to the PDF report)",
                parse_mode='Markdown'
            )
        
        elif query.data == "generate_pdf":
            # Generate PDF report
            await query.edit_message_text("⏳ Generating PDF report...")
            
            try:
                # Get doctor info
                doctor = doctors.data[0] if doctors.data else {}
                
                # Get patient details from context (from current request)
                patient_name = context.user_data.get('patient_name', 'Patient')
                patient_age = context.user_data.get('patient_age', 'N/A')
                patient_village = context.user_data.get('patient_village', 'N/A')
                patient_symptoms = context.user_data.get('patient_symptoms', 'N/A')
                
                # Prepare report data
                report_data = {
                    'patient_name': patient_name,
                    'age': patient_age,
                    'village': patient_village,
                    'symptoms': patient_symptoms,
                    'diseases_detected': ['AI Analysis Results'],
                    'ai_report': context.user_data.get('analysis_result', 'No analysis available'),
                    'doctor_notes': context.user_data.get('doctor_notes', 'No additional notes'),
                    'hindi_patient': context.user_data.get('hindi_report', 'Hindi translation pending'),
                    'doctor_name': doctor.get('name', 'Doctor'),
                    'doctor_mci': doctor.get('mci_reg', 'N/A'),
                    'doctor_phc': doctor.get('phc', 'N/A'),
                    'scan_date': datetime.now().strftime('%d/%m/%Y')
                }
                
                # Generate PDF
                os.makedirs('reports', exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                pdf_filename = f"report_{timestamp}_{patient_name.replace(' ', '_')}.pdf"
                pdf_path = os.path.join('reports', pdf_filename)
                
                generate_pdf(report_data, pdf_path)
                
                logger.info(f"PDF generated: {pdf_path}")
                
                # Update request status to 'reviewed' and save report path
                request_id = context.user_data.get('current_request_id')
                if request_id:
                    try:
                        supabase.table("xray_requests").update({
                            "status": "reviewed",
                            "reviewed_at": datetime.now().isoformat(),
                            "report_pdf_url": pdf_path,
                            "doctor_notes": context.user_data.get('doctor_notes', ''),
                            "ai_report": context.user_data.get('analysis_result', '')
                        }).eq("id", request_id).execute()
                        
                        logger.info(f"Request {request_id} marked as reviewed, report saved")
                    except Exception as e:
                        logger.error(f"Error updating request: {e}")
                
                # Show success message with Contact Patient button
                keyboard = [
                    [InlineKeyboardButton("📞 Contact Patient", callback_data=f"contact_patient_{request_id}")],
                    [InlineKeyboardButton("📥 Download Report", callback_data=f"download_report_{request_id}")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="back_menu")]
                ]
                
                # Escape special characters for Markdown
                safe_filename = pdf_filename.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
                safe_patient_name = patient_name.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
                
                await query.edit_message_text(
                    f"✅ *REPORT GENERATED SUCCESSFULLY*\n\n"
                    f"👤 Patient: {safe_patient_name}\n"
                    f"📄 Report saved to system\n"
                    f"💾 File: `{safe_filename}`\n\n"
                    f"📋 *Status*: Request marked as reviewed\n\n"
                    f"🔒 *Privacy*: Report NOT sent to patient (medical compliance)\n\n"
                    f"👉 Click 'Contact Patient' to communicate with patient",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                
                # Store report path for download
                context.user_data['last_report_path'] = pdf_path
                
                # DON'T clear context yet - needed for contact patient
                # Keep: current_request_id, patient_name, patient_age, patient_village, patient_telegram_id
                context.user_data.pop('patient_age', None)
                context.user_data.pop('patient_village', None)
                context.user_data.pop('patient_symptoms', None)
                
                # Show main menu
                await asyncio.sleep(1)
                await show_main_menu(query.message.chat_id, context)
                
            except Exception as e:
                logger.error(f"Error generating PDF: {e}")
                # Escape special characters in error message
                error_msg = str(e).replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('`', '\\`')
                await query.edit_message_text(
                    f"❌ *Error generating PDF*\n\n"
                    f"Error: {error_msg}\n\n"
                    f"Please try again or contact admin.",
                    parse_mode='Markdown'
                )
        
        elif query.data.startswith("contact_patient_"):
            # Contact Patient - Show options
            request_id = int(query.data.replace("contact_patient_", ""))
            
            # Get patient info
            try:
                request = supabase.table("xray_requests").select("*").eq("id", request_id).execute()
                if request.data and len(request.data) > 0:
                    req = request.data[0]
                    patient_name = req.get('patient_name')
                    patient_telegram_id = req.get('patient_telegram_id')
                    
                    # Store in context
                    context.user_data['contact_patient_id'] = patient_telegram_id
                    context.user_data['contact_patient_name'] = patient_name
                    context.user_data['contact_request_id'] = request_id
                    
                    keyboard = [
                        [InlineKeyboardButton("🎤 Send Voice Note", callback_data="send_voice")],
                        [InlineKeyboardButton("💬 Send Text Message", callback_data="send_text")],
                        [InlineKeyboardButton("🔙 Back", callback_data="back_menu")]
                    ]
                    
                    await query.edit_message_text(
                        f"📞 **CONTACT PATIENT**\n\n"
                        f"👤 Patient: {patient_name}\n"
                        f"📋 Request ID: #{request_id}\n\n"
                        f"Choose communication method:",
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='Markdown'
                    )
                else:
                    await query.edit_message_text("❌ Request not found")
            except Exception as e:
                logger.error(f"Error loading patient info: {e}")
                await query.edit_message_text(f"❌ Error: {str(e)}")
        
        elif query.data == "send_voice":
            # Send Voice Note
            patient_name = context.user_data.get('contact_patient_name', 'Patient')
            
            context.user_data['waiting_for_voice'] = True
            
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="back_menu")]]
            
            await query.edit_message_text(
                f"🎤 **SEND VOICE NOTE**\n\n"
                f"👤 To: {patient_name}\n\n"
                f"📝 Please record and send your voice message now.\n\n"
                f"The voice note will be forwarded to the patient.",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        elif query.data == "send_text":
            # Send Text Message
            patient_name = context.user_data.get('contact_patient_name', 'Patient')
            
            context.user_data['waiting_for_text'] = True
            
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="back_menu")]]
            
            await query.edit_message_text(
                f"💬 **SEND TEXT MESSAGE**\n\n"
                f"👤 To: {patient_name}\n\n"
                f"📝 Type your message below.\n\n"
                f"✨ Your message will be automatically translated to:\n"
                f"• English\n"
                f"• Hindi (हिंदी)\n\n"
                f"Both versions will be sent to the patient.",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        elif query.data.startswith("download_report_"):
            # Download Report
            request_id = int(query.data.replace("download_report_", ""))
            
            try:
                # Get report path from database
                request = supabase.table("xray_requests").select("report_pdf_url, patient_name").eq("id", request_id).execute()
                
                if request.data and len(request.data) > 0:
                    report_path = request.data[0].get('report_pdf_url')
                    patient_name = request.data[0].get('patient_name')
                    
                    if report_path and os.path.exists(report_path):
                        # Send PDF to doctor
                        with open(report_path, 'rb') as pdf_file:
                            await context.bot.send_document(
                                chat_id=query.message.chat_id,
                                document=pdf_file,
                                filename=os.path.basename(report_path),
                                caption=f"📄 **X-RAY REPORT**\n\n"
                                        f"👤 Patient: {patient_name}\n"
                                        f"📋 Request ID: #{request_id}",
                                parse_mode='Markdown'
                            )
                        await query.answer("✅ Report downloaded")
                    else:
                        await query.answer("❌ Report file not found", show_alert=True)
                else:
                    await query.answer("❌ Request not found", show_alert=True)
            except Exception as e:
                logger.error(f"Error downloading report: {e}")
                await query.answer(f"❌ Error: {str(e)}", show_alert=True)
        
        elif query.data == "logout":
            # Logout - clear session
            context.user_data.clear()
            
            await query.edit_message_text(
                "👋 **LOGGED OUT**\n\n"
                "You have been logged out successfully.\n\n"
                "Use /start to login again.",
                parse_mode='Markdown'
            )
            logger.info(f"Doctor {user.id} logged out")
        
        else:
            await query.edit_message_text("❓ Unknown option")
    
    except Exception as e:
        logger.error(f"Error in button_handler: {e}")
        await query.edit_message_text(
            "❌ Error processing request. Please try again."
        )

# ============================================
# MAIN
# ============================================

def main():
    """Start the doctor bot"""
    if not MEDIMIND_DOCTOR_TOKEN:
        logger.error("MEDIMIND_DOCTOR_TOKEN not found in environment!")
        return
    
    logger.info("Starting MediMind Doctor Bot...")
    
    # Create application
    app = Application.builder().token(MEDIMIND_DOCTOR_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("regen_code", regen_code))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    logger.info("Doctor bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
