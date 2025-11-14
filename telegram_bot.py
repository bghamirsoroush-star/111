import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from ultimate_bomber_vip import UltimateBomberVIP
import urllib3

# غیرفعال کردن هشدارهای SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# دریافت توکن از محیط
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8503866458:AAHQCSoHmYRFiKbhEId49_TUtjcA24iGbA0")

# ایجاد نمونه بمب‌افکن
bomber = UltimateBomberVIP()

# دیکشنری برای ذخیره وضعیت کاربران
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع"""
    user_id = update.effective_user.id
    user_sessions[user_id] = {
        "phone": None, 
        "attack_type": None, 
        "requests": 150,
        "status": "آماده"
    }
    
    welcome_text = """
🎯 **Ultimate Bomber VIP PRO** 🚀

⚡ *قدرتمندترین بمب‌افکن پیامک و تماس با 50+ سرویس فعال*

✨ **ویژگی‌های جدید:**
• 🚀 30+ سرویس پیامک جدید
• 📞 20+ سرویس تماس جدید  
• 💎 سرعت 2x بهبود یافته
• 🎯 دقت 95% موفقیت
• ⚡ پاسخگویی فوق سریع

💎 **دستورات VIP PRO:**
🔹 /bomb - شروع حمله جدید
🔹 /quick - حمله سریع پیش‌فرض
🔹 /stop - توقف حمله فعلی  
🔹 /status - وضعیت لحظه‌ای
🔹 /help - راهنمای کامل

🎪 **انواع حمله PRO:**
• 🚀 SMS Bomber VIP - 30+ سرویس
• 📞 Call Bomber VIP - 20+ سرویس  
• 💎 Super VIP - ترکیب 50+ سرویس

⚠️ **توجه:** این ربات فقط برای اهداف آموزشی ارائه شده است.
    """
    
    keyboard = [
        [InlineKeyboardButton("🚀 شروع حمله جدید", callback_data="start_attack")],
        [InlineKeyboardButton("⚡ حمله سریع", callback_data="quick_attack")],
        [InlineKeyboardButton("📊 وضعیت سیستم", callback_data="system_status")],
        [InlineKeyboardButton("ℹ️ راهنمای کامل", callback_data="full_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def bomb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع حمله جدید"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "phone": None, 
            "attack_type": None, 
            "requests": 150,
            "status": "آماده"
        }
    
    if context.args:
        phone = context.args[0]
        user_sessions[user_id]["phone"] = phone
        await ask_attack_type(update, context)
        return
    
    keyboard = [
        [InlineKeyboardButton("📱 وارد کردن شماره", callback_data="enter_number")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 **حمله جدید**\n\n📱 **لطفا شماره تلفن را وارد کنید:**\n\n"
        "• فرمت: `09123456789`\n"
        "• یا از دکمه زیر استفاده کنید", 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def quick_attack_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حمله سریع با شماره‌های پیش‌فرض"""
    keyboard = [
        [
            InlineKeyboardButton("🎭 یاسینی", callback_data="quick_yasini"),
            InlineKeyboardButton("🎯 حسنی", callback_data="quick_hasani")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚡ **حمله سریع Super VIP**\n\n"
        "🎯 انتخاب شماره هدف از لیست پیش‌فرض:\n\n"
        "• 🎭 یاسینی: `09335037492`\n"
        "• 🎯 حسنی: `09122805035`\n\n"
        "⚠️ این حمله با حداکثر قدرت اجرا می‌شود",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def ask_attack_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پرسش نوع حمله"""
    keyboard = [
        [
            InlineKeyboardButton("🚀 SMS VIP", callback_data="sms_vip"),
            InlineKeyboardButton("📞 CALL VIP", callback_data="call_vip")
        ],
        [InlineKeyboardButton("💎 SUPER VIP", callback_data="super_vip")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 **انتخاب نوع حمله VIP PRO**\n\n"
        "• 🚀 **SMS Bomber VIP** - 30+ سرویس پیامک\n"
        "• 📞 **Call Bomber VIP** - 20+ سرویس تماس\n"  
        "• 💎 **Super VIP** - ترکیب 50+ سرویس\n\n"
        "⚡ قدرت: Super VIP > SMS VIP > Call VIP",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت دکمه‌های اینلاین"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "phone": None, 
            "attack_type": None, 
            "requests": 150,
            "status": "آماده"
        }
    
    if data == "main_menu":
        await start(query, context)
        return
    elif data == "start_attack":
        await bomb_handler(query, context)
        return
    elif data == "quick_attack":
        await quick_attack_handler(query, context)
        return
    elif data == "system_status":
        await status_handler(query, context)
        return
    elif data == "full_help":
        await help_handler(query, context)
        return
    elif data == "enter_number":
        await query.message.reply_text(
            "📱 **لطفا شماره تلفن را ارسال کنید:**\n\nمثال: `09123456789`",
            parse_mode='Markdown'
        )
        return
    elif data in ["quick_yasini", "quick_hasani"]:
        preset_name = "yasini" if data == "quick_yasini" else "hasani"
        await execute_quick_attack(query, preset_name)
        return
    elif data in ["sms_vip", "call_vip", "super_vip"]:
        user_sessions[user_id]["attack_type"] = data
        await ask_requests_count(query)
    elif data.startswith("requests_"):
        requests_count = int(data.split("_")[1])
        user_sessions[user_id]["requests"] = requests_count
        await start_attack(query)

async def execute_quick_attack(query, preset_name):
    """اجرای حمله سریع"""
    preset_info = {
        "yasini": {"name": "زمانی", "number": "09335037492", "icon": "🎭"},
        "hasani": {"name": "حسنی", "number": "09122805035", "icon": "🎯"}
    }
    
    info = preset_info[preset_name]
    
    status_text = f"""
{info['icon']} **شروع حمله سریع Super VIP**

📞 شماره: `{info['number']}`
🎯 هدف: {info['name']}
💎 نوع: Super VIP
🔢 تعداد: 300 درخواست
⚡ وضعیت: در حال اجرا...

⏳ لطفا منتظر بمانید، این عملیات ممکن است 2-3 دقیقه طول بکشد.
    """
    
    status_message = await query.message.reply_text(status_text, parse_mode='Markdown')
    
    try:
        user_sessions[query.from_user.id]["status"] = "در حال اجرا"
        
        result = bomber.quick_attack_preset(preset_name)
        
        if "error" in result:
            await status_message.edit_text(
                f"❌ **خطا در اجرای حمله:**\n\n`{result['error']}`",
                parse_mode='Markdown'
            )
        else:
            result_text = f"""
🎉 **حمله سریع Super VIP تکمیل شد!** ✅

{info['icon']} **هدف:** {info['name']}
📞 شماره: `{result['phone']}`
⏱️ زمان اجرا: {result['duration']}
📊 کل درخواست‌ها: {result['total_requests']}
✅ درخواست‌های موفق: {result['successful']}
❌ درخواست‌های ناموفق: {result['failed']}
🎯 نرخ موفقیت: {result['success_rate']}
⚡ سرعت متوسط: {result['speed']}

🏆 **سرویس‌های فعال شده:**
"""
            
            if result.get('working_services'):
                for service in result['working_services']:
                    result_text += f"• {service}\n"
            else:
                result_text += "• هیچ سرویس فعالی یافت نشد\n"
            
            result_text += f"\n🔄 برای حمله جدید /bomb را ارسال کنید"
            
            keyboard = [
                [InlineKeyboardButton("🔄 حمله مجدد", callback_data=f"quick_{preset_name}")],
                [InlineKeyboardButton("🎯 حمله جدید", callback_data="start_attack")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await status_message.edit_text(result_text, parse_mode='Markdown', reply_markup=reply_markup)
        
        user_sessions[query.from_user.id]["status"] = "تکمیل شده"
            
    except Exception as e:
        await status_message.edit_text(
            f"❌ **خطای غیرمنتظره:**\n\n`{str(e)}`\n\n"
            "لطفا بعدا دوباره تلاش کنید.",
            parse_mode='Markdown'
        )
        user_sessions[query.from_user.id]["status"] = "خطا"

async def ask_requests_count(query):
    """پرسش تعداد درخواست‌ها"""
    user_id = query.from_user.id
    attack_type = user_sessions[user_id]["attack_type"]
    
    # تنظیم تعداد درخواست پیش‌فرض بر اساس نوع حمله
    if attack_type == "sms_vip":
        default_requests = 150
        max_requests = 200
    elif attack_type == "call_vip":
        default_requests = 120
        max_requests = 180
    else:
        default_requests = 250
        max_requests = 300
    
    keyboard = [
        [
            InlineKeyboardButton(f"⚡ {default_requests}", callback_data=f"requests_{default_requests}"),
            InlineKeyboardButton(f"🚀 {max_requests}", callback_data=f"requests_{max_requests}")
        ],
        [
            InlineKeyboardButton("🔙 بازگشت", callback_data="start_attack")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    attack_name = {
        "sms_vip": "SMS Bomber VIP",
        "call_vip": "Call Bomber VIP", 
        "super_vip": "Super VIP"
    }.get(user_sessions[user_id]["attack_type"])
    
    await query.message.reply_text(
        f"🔢 **تعداد درخواست‌ها برای {attack_name}**\n\n"
        f"• ⚡ {default_requests} درخواست - پیشنهادی\n"
        f"• 🚀 {max_requests} درخواست - حداکثر قدرت\n\n"
        f"💡 تعداد بیشتر = قدرت بیشتر + زمان بیشتر",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_attack(query):
    """شروع عملیات حمله"""
    user_id = query.from_user.id
    user_data = user_sessions.get(user_id, {})
    phone = user_data.get("phone")
    attack_type = user_data.get("attack_type", "sms_vip")
    requests_count = user_data.get("requests", 150)
    
    if not phone:
        await query.message.reply_text("❌ **خطا:** شماره تلفن تنظیم نشده است!")
        return
    
    # نمایش اطلاعات حمله
    attack_info = {
        "sms_vip": {"name": "SMS Bomber VIP", "icon": "🚀"},
        "call_vip": {"name": "Call Bomber VIP", "icon": "📞"},
        "super_vip": {"name": "Super VIP", "icon": "💎"}
    }.get(attack_type, {"name": "SMS Bomber VIP", "icon": "🚀"})
    
    info_text = f"""
{attack_info['icon']} **شروع حمله {attack_info['name']}**

📞 شماره: `{phone}`
🎯 نوع: {attack_info['name']}
🔢 تعداد: {requests_count} درخواست
⚡ وضعیت: در حال اجرا...

⏳ لطفا منتظر بمانید، این عملیات ممکن است چند دقیقه طول بکشد.
    """
    
    status_message = await query.message.reply_text(info_text, parse_mode='Markdown')
    
    try:
        user_sessions[user_id]["status"] = "در حال اجرا"
        
        # شروع حمله بر اساس نوع
        if attack_type == "sms_vip":
            result = bomber.start_sms_bomber_vip(phone, requests_count)
        elif attack_type == "call_vip":
            result = bomber.start_call_bomber_vip(phone, requests_count)
        else:
            result = bomber.start_super_vip(phone, requests_count)
        
        if "error" in result:
            await status_message.edit_text(
                f"❌ **خطا در اجرای حمله:**\n\n`{result['error']}`\n\n"
                "لطفا دوباره تلاش کنید یا شماره دیگری وارد کنید.",
                parse_mode='Markdown'
            )
        else:
            # ساخت متن نتیجه
            result_text = f"""
🎉 **حمله {attack_info['name']} تکمیل شد!** ✅

📞 شماره: `{result['phone']}`
⏱️ زمان اجرا: {result['duration']}
📊 کل درخواست‌ها: {result['total_requests']}
✅ درخواست‌های موفق: {result['successful']}
❌ درخواست‌های ناموفق: {result['failed']}
🎯 نرخ موفقیت: {result['success_rate']}
⚡ سرعت متوسط: {result['speed']}

🏆 **سرویس‌های فعال شده:**
"""
            
            if result.get('working_services'):
                for service in result['working_services']:
                    result_text += f"• {service}\n"
            else:
                result_text += "• هیچ سرویس فعالی یافت نشد\n"
            
            result_text += f"\n🔄 برای حمله جدید /bomb را ارسال کنید"
            
            keyboard = [
                [InlineKeyboardButton("🔄 حمله مجدد", callback_data="start_attack")],
                [InlineKeyboardButton("⚡ حمله سریع", callback_data="quick_attack")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await status_message.edit_text(result_text, parse_mode='Markdown', reply_markup=reply_markup)
        
        user_sessions[user_id]["status"] = "تکمیل شده"
            
    except Exception as e:
        await status_message.edit_text(
            f"❌ **خطای غیرمنتظره:**\n\n`{str(e)}`\n\n"
            "لطفا بعدا دوباره تلاش کنید.",
            parse_mode='Markdown'
        )
        user_sessions[user_id]["status"] = "خطا"

async def stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """توقف حمله"""
    user_id = update.effective_user.id
    user_sessions[user_id]["status"] = "متوقف شده"
    
    bomber.stop_attack()
    
    keyboard = [
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")],
        [InlineKeyboardButton("🎯 حمله جدید", callback_data="start_attack")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🛑 **حمله متوقف شد**\n\n"
        "تمام عملیات‌های در حال اجرا متوقف شدند.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وضعیت فعلی"""
    user_id = update.effective_user.id
    user_data = user_sessions.get(user_id, {})
    
    # محاسبه آمار پیشرفته
    total_attempts = bomber.success_count + bomber.failed_count
    success_rate = (bomber.success_count / total_attempts * 100) if total_attempts > 0 else 0
    
    status_text = f"""
📊 **وضعیت سیستم Ultimate Bomber VIP PRO**

👤 **وضعیت کاربر:**
• 🔄 وضعیت: {user_data.get('status', 'ناشناخته')}
• 📞 شماره هدف: `{user_data.get('phone', 'تنظیم نشده')}`
• 🎯 نوع حمله: {user_data.get('attack_type', 'تنظیم نشده')}
• 🔢 تعداد درخواست: {user_data.get('requests', 0)}

📈 **آمار کلی سیستم:**
• ✅ درخواست‌های موفق: {bomber.success_count:,}
• ❌ درخواست‌های ناموفق: {bomber.failed_count:,}
• 📊 مجموع درخواست‌ها: {total_attempts:,}
• 🎯 نرخ موفقیت: {success_rate:.1f}%
• 🟢 وضعیت سیستم: فعال

💡 **دستورات سریع:**
• /bomb - حمله جدید
• /quick - حمله سریع
• /stop - توقف حمله
"""

    keyboard = [
        [InlineKeyboardButton("🎯 حمله جدید", callback_data="start_attack")],
        [InlineKeyboardButton("⚡ حمله سریع", callback_data="quick_attack")],
        [InlineKeyboardButton("🔄 رفرش", callback_data="system_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if isinstance(update, Update):
        await update.message.reply_text(status_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(status_text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنمای کامل"""
    help_text = """
📖 **راهنمای Ultimate Bomber VIP PRO**

🎯 **دستورات اصلی:**
• /start - شروع کار با ربات
• /bomb [شماره] - شروع حمله جدید
• /quick - حمله سریع پیش‌فرض
• /stop - توقف حمله فعلی
• /status - وضعیت لحظه‌ای سیستم
• /help - نمایش این راهنما

⚡ **انواع حمله PRO:**
• 🚀 **SMS Bomber VIP** - 30+ سرویس پیامک
• 📞 **Call Bomber VIP** - 20+ سرویس تماس  
• 💎 **Super VIP** - ترکیب 50+ سرویس

🎪 **حمله سریع:**
• شماره‌های پیش‌فرض یاسینی و حسنی
• اجرای خودکار با حداکثر قدرت
• مناسب برای تست سریع

📱 **نحوه استفاده:**
1. شماره تلفن را وارد کنید (با /bomb یا مستقیم)
2. نوع حمله VIP را انتخاب کنید
3. تعداد درخواست‌ها را مشخص کنید
4. منتظر نتیجه بمانید

⚠️ **نکات مهم:**
• این ربات فقط برای اهداف آموزشی است
• سرعت بستگی به سرور و سرویس‌ها دارد
• از استفاده غیراخلاقی خودداری کنید
• اطلاعات شما محفوظ می‌ماند

🔧 **پشتیبانی:** در صورت مشکل با دستور /start مجدد تلاش کنید.
    """
    
    keyboard = [
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")],
        [InlineKeyboardButton("🎯 شروع حمله", callback_data="start_attack")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if isinstance(update, Update):
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های متنی"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "phone": None, 
            "attack_type": None, 
            "requests": 150,
            "status": "آماده"
        }
    
    # اگر متن شامل شماره است
    if any(c.isdigit() for c in text) and len(text) >= 10:
        user_sessions[user_id]["phone"] = text
        await ask_attack_type(update, context)
    else:
        keyboard = [
            [InlineKeyboardButton("🎯 شروع حمله", callback_data="start_attack")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ **شماره تلفن معتبر نیست!**\n\n"
            "لطفا یک شماره تلفن معتبر ایرانی وارد کنید:\n"
            "مثال: `09123456789`\n\n"
            "یا از دکمه زیر استفاده کنید:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاها"""
    logger.error(f"Error: {context.error}")
    
    try:
        keyboard = [
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ **خطای سیستمی رخ داد!**\n\n"
            "لطفا دوباره تلاش کنید یا از /start استفاده نمایید.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except:
        pass

def main():
    """تابع اصلی اجرای ربات"""
    if not TOKEN:
        print("❌ توکن ربات یافت نشد!")
        return
    
    # ایجاد اپلیکیشن تلگرام
    app = Application.builder().token(TOKEN).build()
    
    # اضافه کردن handlerها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", bomb_handler))
    app.add_handler(CommandHandler("quick", quick_attack_handler))
    app.add_handler(CommandHandler("stop", stop_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # اضافه کردن handler خطا
    app.add_error_handler(error_handler)
    
    # شروع ربات
    print("🎯 Ultimate Bomber VIP PRO Bot Started...")
    print("🤖 Bot is now listening for messages...")
    print("🔗 Token:", TOKEN[:10] + "..." if TOKEN else "Not Found")
    print("💎 Enhanced with 50+ services and quick attack feature")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
