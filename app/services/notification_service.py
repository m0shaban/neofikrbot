import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# إعدادات البريد الإلكتروني
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'your_email@gmail.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'your_app_password')

# إعدادات واتساب
WHATSAPP_API_KEY = os.environ.get('WHATSAPP_API_KEY', 'your_whatsapp_api_key')
WHATSAPP_PHONE_ID = os.environ.get('WHATSAPP_PHONE_ID', 'your_whatsapp_phone_id')

# إعدادات تيليجرام
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'your_telegram_chat_id')

def send_email(to_email, subject, body):
    """
    إرسال بريد إلكتروني باستخدام SMTP
    
    Args:
        to_email (str): عنوان البريد الإلكتروني للمستلم
        subject (str): موضوع البريد الإلكتروني
        body (str): محتوى البريد الإلكتروني
        
    Returns:
        bool: نجاح أو فشل عملية الإرسال
    """
    try:
        # إنشاء رسالة البريد الإلكتروني
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # إضافة نص الرسالة
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # الاتصال بخادم SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            # تسجيل الدخول إلى الخادم
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            # إرسال البريد الإلكتروني
            server.send_message(msg)
            
        print(f"تم إرسال البريد الإلكتروني بنجاح إلى {to_email}")
        return True
    
    except Exception as e:
        print(f"خطأ في إرسال البريد الإلكتروني: {e}")
        return False

def send_whatsapp(to_number, message):
    """
    إرسال رسالة واتساب باستخدام WhatsApp Business API
    
    Args:
        to_number (str): رقم الهاتف المستلم بتنسيق دولي (مثل 201121891913)
        message (str): نص الرسالة
        
    Returns:
        bool: نجاح أو فشل عملية الإرسال
    """
    try:
        # في حالة عدم توفر أو تكوين API واتساب، سنقوم بتسجيل الرسالة فقط
        if WHATSAPP_API_KEY == 'your_whatsapp_api_key':
            print(f"[محاكاة واتساب] إرسال إلى {to_number}: {message}")
            return True
            
        # تأكد من وجود تنسيق بادئة الدولة ل to_number (مثل 201121891913)
        if not to_number.startswith('2'):
            to_number = '2' + to_number
            
        # إعداد طلب API واتساب
        url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # بيانات الرسالة
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        # إرسال الطلب إلى API واتساب
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"تم إرسال رسالة واتساب بنجاح إلى {to_number}")
            return True
        else:
            print(f"فشل إرسال رسالة واتساب: {response.text}")
            return False
            
    except Exception as e:
        print(f"خطأ في إرسال رسالة واتساب: {e}")
        return False

def send_telegram(message):
    """
    إرسال رسالة عبر بوت تيليجرام
    
    Args:
        message (str): محتوى الرسالة
        
    Returns:
        bool: نجاح أو فشل عملية الإرسال
    """
    try:
        # في حالة عدم توفر بيانات تيليجرام، سنقوم بتسجيل الرسالة فقط
        if TELEGRAM_BOT_TOKEN == 'your_telegram_bot_token':
            print(f"[محاكاة تيليجرام] إرسال إلى {TELEGRAM_CHAT_ID}: {message}")
            return True
            
        # إعداد طلب API تيليجرام
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        # إرسال الطلب إلى API تيليجرام
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print(f"تم إرسال رسالة تيليجرام بنجاح")
            return True
        else:
            print(f"فشل إرسال رسالة تيليجرام: {response.text}")
            return False
            
    except Exception as e:
        print(f"خطأ في إرسال رسالة تيليجرام: {e}")
        return False