from flask import Blueprint, request, jsonify
import os
import requests
import json
from app import db
from app.models.customer import Customer
from app.models.order import Order
from app.services.deepseek_service import process_with_deepseek
from app.services.notification_service import send_email, send_whatsapp, send_telegram
from datetime import datetime

webhook_bp = Blueprint('webhook', __name__)

# تكوين معرف التحقق وتوكن صفحة فيسبوك
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'your_verify_token')
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN', 'your_page_access_token')

@webhook_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """التحقق من صحة الويب هوك عند إعداده على فيسبوك"""
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'فشل التحقق من صحة التوكن', 403

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """معالجة الرسائل الواردة من فيسبوك"""
    data = request.json
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                
                # الحصول على معلومات المستخدم من فيسبوك
                user_info = get_user_info(sender_id)
                
                if 'message' in messaging_event:
                    handle_message(sender_id, messaging_event['message'], user_info)
                elif 'postback' in messaging_event:
                    handle_postback(sender_id, messaging_event['postback'], user_info)
                    
    return 'OK', 200

def get_user_info(sender_id):
    """الحصول على معلومات المستخدم من فيسبوك"""
    url = f"https://graph.facebook.com/{sender_id}"
    params = {
        "fields": "first_name,last_name,profile_pic",
        "access_token": PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print(f"خطأ في الحصول على معلومات المستخدم: {e}")
        return {}

def handle_message(sender_id, message, user_info):
    """معالجة الرسائل النصية الواردة"""
    if 'text' not in message:
        # إذا لم تكن رسالة نصية، أرسل رسالة تطلب رسالة نصية
        send_message(sender_id, "أرجو إرسال رسالة نصية.")
        return

    text = message['text']
    
    # معالجة النص باستخدام DeepSeek API
    response_text = process_with_deepseek(text, user_info)
    
    # التحقق من وجود نية لتقديم طلب
    if "طلب" in text or "خدمة" in text or "اطلب" in text or "سعر" in text or "استشارة" in text:
        # حفظ الطلب المحتمل
        save_order(sender_id, text, user_info)
        
        # إرسال إشعار للإدارة
        send_notification(sender_id, text, user_info)
    
    # الرد على المستخدم
    send_message(sender_id, response_text)

def handle_postback(sender_id, postback, user_info):
    """معالجة الردود من القوائم والأزرار"""
    payload = postback['payload']
    
    if payload == 'GET_STARTED':
        welcome_message = "مرحبًا 👋 معك شات بوت شركة NeoFikr Solutions 🚀\n\n"
        welcome_message += "نقدّم لك حلولًا ذكية تساعدك على تطوير عملك باستخدام الذكاء الاصطناعي والتحول الرقمي.\n\n"
        welcome_message += "اختر من القائمة التالية👇 أو اكتب رقم الخدمة التي تهمك:\n\n"
        welcome_message += "1️⃣ خدمات الشركة\n"
        welcome_message += "2️⃣ تحميل دليل أدوات الذكاء الاصطناعي\n"
        welcome_message += "3️⃣ مشاهدة الكورسات والدورات\n"
        welcome_message += "4️⃣ طلب استشارة أو عرض سعر\n"
        welcome_message += "5️⃣ التحدث مع أحد أعضاء الفريق\n"
        welcome_message += "📞 رقم التواصل: 01121891913"
        
        send_message(sender_id, welcome_message)
        
        # تخزين العميل في قاعدة البيانات
        save_customer(sender_id, user_info)
    
    elif payload == 'SERVICES':
        services_message = "خدمات الشركة نوفر مجموعة من الخدمات الذكية:\n"
        services_message += "🔹 تصميم شات بوت احترافي\n"
        services_message += "🔹 إنشاء CRM مخصص لإدارة العملاء\n"
        services_message += "🔹 أدوات تحليل بيانات ومراقبة الأداء\n"
        services_message += "🔹 أتمتة العمليات الرقمية\n"
        services_message += "🔹 تصميم واجهات ذكية للتطبيقات\n"
        services_message += "🔹 استشارات وتدريب في الذكاء الاصطناعي\n\n"
        services_message += "اكتب رقم الخدمة لمزيد من التفاصيل."
        
        send_message(sender_id, services_message)

def save_customer(sender_id, user_info):
    """تخزين معلومات العميل في قاعدة البيانات"""
    try:
        # التحقق من وجود العميل
        customer = Customer.query.filter_by(facebook_id=sender_id).first()
        
        if not customer:
            name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"
            customer = Customer(
                facebook_id=sender_id,
                name=name
            )
            db.session.add(customer)
            db.session.commit()
            
        return customer
    except Exception as e:
        print(f"خطأ في حفظ معلومات العميل: {e}")
        db.session.rollback()
        return None

def save_order(sender_id, text, user_info):
    """تخزين الطلب في قاعدة البيانات"""
    try:
        # الحصول على العميل أو إنشاء عميل جديد
        customer = save_customer(sender_id, user_info)
        
        if customer:
            # تحديد نوع الخدمة من الرسالة
            service_type = "استفسار عام"
            if "شات بوت" in text.lower() or "chatbot" in text.lower():
                service_type = "شات بوت"
            elif "crm" in text.lower() or "ادارة العملاء" in text.lower():
                service_type = "CRM"
            elif "تحليل" in text.lower() or "بيانات" in text.lower():
                service_type = "تحليل بيانات"
            elif "اتمتة" in text.lower() or "أتمتة" in text.lower():
                service_type = "أتمتة عمليات"
            elif "تصميم" in text.lower() or "واجهة" in text.lower():
                service_type = "تصميم واجهات"
            elif "تدريب" in text.lower() or "استشارة" in text.lower():
                service_type = "تدريب واستشارات"
            elif "طلب" in text.lower() or "عرض سعر" in text.lower() or "خدمة" in text.lower():
                service_type = "طلب خدمة"
            
            # إنشاء الطلب
            order = Order(
                customer_id=customer.id,
                service_type=service_type,
                details=text,
                status="جديد"  # إضافة حالة الطلب الافتراضية
            )
            db.session.add(order)
            db.session.commit()
            print(f"تم حفظ الطلب بنجاح: {order.id}, العميل: {customer.name}, الخدمة: {service_type}")
            return order
        else:
            print("لم يتم إنشاء الطلب: لم يتم العثور على عميل أو إنشاؤه")
            return None
    except Exception as e:
        print(f"خطأ في حفظ الطلب: {e}")
        db.session.rollback()
        return None

def send_notification(sender_id, text, user_info):
    """إرسال إشعارات للإدارة عن الطلبات الجديدة"""
    try:
        name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"
        
        # حفظ الطلب في قاعدة البيانات وإشعار للإدارة
        order = save_order(sender_id, text, user_info)
        
        if not order:
            print("فشل حفظ الطلب، سيتم محاولة إرسال الإشعارات فقط")
        
        # إعداد نص الإشعار
        subject = f"طلب جديد من {name} - NeoFikr Chatbot"
        now_formatted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # رسالة تيليجرام منسقة
        telegram_message = f"""<b>🔔 طلب جديد من الشات بوت!</b>

🧑‍💼 <b>اسم العميل:</b> {name}
📱 <b>معرف فيسبوك:</b> {sender_id}
⏰ <b>التاريخ:</b> {now_formatted}
🏷️ <b>نوع الخدمة:</b> {order.service_type if order else "غير محدد"}
🆔 <b>رقم الطلب:</b> {order.id if order else "لم يتم التسجيل"}

<b>📝 الرسالة:</b>
<pre>{text}</pre>

<i>يمكنك إدارة هذا الطلب من خلال <a href="http://admin.neofikr.com/orders">لوحة التحكم</a>.</i>
"""
        
        # محاولة الإرسال عبر تيليجرام (الوسيلة الرئيسية)
        telegram_sent = send_telegram(telegram_message)
        
        if telegram_sent:
            print("تم إرسال إشعار تيليجرام بنجاح")
        else:
            print("⚠️ فشل إرسال إشعار تيليجرام!")
        
        # إعداد نص البريد الإلكتروني
        body = f"""
        طلب جديد من الشات بوت:
        
        الاسم: {name}
        معرف فيسبوك: {sender_id}
        التاريخ: {now_formatted}
        نوع الخدمة: {order.service_type if order else "غير محدد"}
        رقم الطلب: {order.id if order else "لم يتم التسجيل"}
        
        الرسالة:
        {text}
        
        يمكنك إدارة هذا الطلب من خلال لوحة التحكم:
        http://admin.neofikr.com/orders
        """
        
        # محاولة الإرسال عبر البريد الإلكتروني (اختياري)
        try:
            email_sent = send_email('neofikrsolutions@gmail.com', subject, body)
            if email_sent:
                print("تم إرسال البريد الإلكتروني بنجاح")
        except Exception as e:
            print(f"فشل إرسال البريد الإلكتروني: {e}")
        
        # محاولة الإرسال عبر واتساب (اختياري)
        try:
            # إعداد رسالة واتساب موجزة
            whatsapp_message = f"🔔 *طلب جديد*\n👤 {name}\n📝 {text[:100]}...\n🕒 {now_formatted}"
            whatsapp_sent = send_whatsapp('01121891913', whatsapp_message)
            if whatsapp_sent:
                print("تم إرسال رسالة واتساب بنجاح")
        except Exception as e:
            print(f"فشل إرسال رسالة واتساب: {e}")
            
        # إضافة تسجيل يوضح أن الطلب تم إشعار الإدارة به
        if order:
            order.notified = True
            db.session.commit()
            print(f"تم تحديث حالة الإشعار للطلب {order.id}")
            
        return True
            
    except Exception as e:
        print(f"خطأ في إرسال الإشعارات: {e}")
        return False

def send_message(recipient_id, message_text):
    """إرسال رسالة نصية إلى مستخدم فيسبوك"""
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    }
    url = "https://graph.facebook.com/v19.0/me/messages"
    
    try:
        response = requests.post(url, params=params, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"خطأ في إرسال الرسالة: {e}")
        return None