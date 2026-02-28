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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.doctor')

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MEDIMIND_DOCTOR_TOKEN = os.getenv("MEDIMIND_DOCTOR_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Doctor login/registration"""
    user = update.effective_user
    
    logger.info(f"Doctor bot /start by user {user.id} (@{user.username})")
    
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
                f"Choose an option below:"
            )
            await show_main_menu(update, context)
        else:
            # New doctor registration
            phone = f"+91{user.id}"  # Fallback phone
            context.user_data['phone'] = phone
            context.user_data['step'] = 'profile'
            
            await update.message.reply_text(
                f"👨‍⚕️ **DOCTOR REGISTRATION**\n\n"
                f"📱 Telegram ID: {user.id}\n"
                f"📞 Phone: {phone}\n\n"
                f"Please enter your details in this format:\n\n"
                f"**Name | MCI Reg | PHC Name**\n\n"
                f"Example:\n"
                f"`Dr. Shah | GJMC12345 | Anklav PHC`\n\n"
                f"Send your details now:",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await update.message.reply_text(
            "❌ Error connecting to database. Please try again later."
        )

async def regen_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /regen_code command - Generate new access code"""
    user = update.effective_user
    
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - Profile registration"""
    text = update.message.text
    user = update.effective_user
    
    if context.user_data.get('step') == 'profile':
        # Parse profile format: Name | MCI | PHC
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
                await show_main_menu(update, context)
                
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
    else:
        # Unknown message
        await update.message.reply_text(
            "❓ I don't understand. Use /start to begin."
        )

# ============================================
# MENU FUNCTIONS
# ============================================

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main doctor menu"""
    keyboard = [
        [InlineKeyboardButton("📋 My Queue", callback_data="queue")],
        [InlineKeyboardButton("🩻 Analyze Image", callback_data="analyze")],
        [InlineKeyboardButton("📋 Old Reports", callback_data="old_reports")],
        [InlineKeyboardButton("🔐 Regen Code", callback_data="regen_code_btn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "🎯 **DOCTOR MENU**\n\nChoose an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "🎯 **DOCTOR MENU**\n\nChoose an option:",
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
            ).eq("doctor_phone", phone).order("created_at", desc=True).limit(10).execute()
            
            if requests.data and len(requests.data) > 0:
                text = "📋 **MY QUEUE**\n\n"
                for r in requests.data:
                    status_emoji = "🔴" if r['status'] == 'pending' else "✅"
                    symptoms_short = r['symptoms'][:40] + "..." if r['symptoms'] and len(r['symptoms']) > 40 else r['symptoms']
                    text += f"{status_emoji} **{r['patient_name']}** ({r['age']}y)\n"
                    text += f"   📍 {r.get('village', 'N/A')} | {symptoms_short}\n"
                    text += f"   ID: {r['id']}\n\n"
                
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await query.edit_message_text(
                    text + "👆 Note the ID to analyze specific case",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            else:
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
                await query.edit_message_text(
                    "✅ No X-rays in your queue!\n\nAll cases reviewed.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif query.data == "analyze":
            # Show scan type selection
            keyboard = [
                [InlineKeyboardButton("🫁 X-ray", callback_data="scan_xray")],
                [InlineKeyboardButton("🧠 CT Scan", callback_data="scan_ct"), 
                 InlineKeyboardButton("🩻 MRI", callback_data="scan_mri")],
                [InlineKeyboardButton("🩹 Skin", callback_data="scan_skin")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_menu")]
            ]
            await query.edit_message_text(
                "🏥 **SELECT SCAN TYPE**\n\nWhat type of scan do you want to analyze?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        elif query.data.startswith("scan_"):
            scan_type = query.data.replace("scan_", "").upper()
            await query.edit_message_text(
                f"🩻 **{scan_type} ANALYSIS**\n\n"
                f"Feature coming soon!\n\n"
                f"This will allow you to:\n"
                f"• Upload {scan_type} images\n"
                f"• Get AI analysis\n"
                f"• Add doctor notes\n"
                f"• Generate reports"
            )
            await asyncio.sleep(2)
            await show_main_menu(update, context)
        
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
            await show_main_menu(update, context)
        
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
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    logger.info("Doctor bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
