import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    MAX_THREADS = int(os.getenv("MAX_THREADS", 50))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 15))
    MAX_REQUESTS_PER_USER = int(os.getenv("MAX_REQUESTS_PER_USER", 500))
    
    # تنظیمات امنیتی
    ALLOWED_PHONE_PREFIXES = ['09', '+98', '98', '0098']
    MAX_PHONE_LENGTH = 13
    MIN_PHONE_LENGTH = 10
