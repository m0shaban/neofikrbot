from flask import Blueprint, request, jsonify, current_app
import os
import requests
import json
from app import db
from app.models.customer import Customer
from app.models.order import Order
from app.models.conversation import Conversation
from app.services.deepseek_service import process_with_deepseek
from app.services.notification_service import send_email, send_whatsapp, send_telegram
from datetime import datetime

webhook_bp = Blueprint('webhook', __name__)

# تكوين معرف التحقق وتوكن صفحة فيسبوك
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'your_verify_token')
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN', 'your_page_access_token')

# الدومين الرئيسي للتطبيق - يمكن تغييره من خلال متغيرات البيئة
BASE_DOMAIN = os.environ.get('BASE_DOMAIN', 'https://neofikrbot.onrender.com')

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
                    handle_message(sender_id, messaging_event['message']['text'])
                elif 'postback' in messaging_event:
                    handle_postback(sender_id, messaging_event['postback']['payload'])
                    
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

def handle_message(sender_id, message_text):
    """
    معالجة الرسائل الواردة من المستخدم
    :param sender_id: معرف المرسل
    :param message_text: نص الرسالة
    :return: None
    """
    # حفظ رسالة المستخدم في قاعدة البيانات
    save_conversation(sender_id, 'user', message_text)

    # التحقق مما إذا كانت الرسالة تتعلق بطلب خدمة
    if "طلب" in message_text or "خدمة" in message_text or "service" in message_text.lower() or "order" in message_text.lower():
        # إرسال نموذج طلب الخدمة
        send_order_form(sender_id)
    else:
        # الحصول على رد من DeepSeek
        from app.services.deepseek_service import get_deepseek_response
        response = get_deepseek_response(message_text)
        
        # إرسال الرد إلى المستخدم
        send_message(sender_id, response)
        
        # حفظ رد البوت في قاعدة البيانات
        save_conversation(sender_id, 'bot', response)

def handle_postback(sender_id, payload):
    """
    معالجة الردود من الأزرار
    :param sender_id: معرف المرسل
    :param payload: البيانات المرسلة من الزر
    :return: None
    """
    # حفظ تفاعل المستخدم مع الأزرار في قاعدة البيانات
    save_conversation(sender_id, 'user', f"[POSTBACK: {payload}]")
    
    if payload == 'GET_STARTED':
        # إرسال رسالة ترحيبية
        welcome_message = "مرحباً بك في بوت نيوفكر للذكاء الاصطناعي! 👋\n\nيمكنني مساعدتك في معرفة المزيد عن خدمات نيوفكر في مجال الذكاء الاصطناعي وتحويل الأعمال الرقمي. كيف يمكنني مساعدتك اليوم؟"
        send_message(sender_id, welcome_message)
        
        # حفظ رد البوت في قاعدة البيانات
        save_conversation(sender_id, 'bot', welcome_message)
        
    elif payload == 'ORDER_FORM':
        # إرسال نموذج طلب الخدمة
        send_order_form(sender_id)
        
    elif payload == 'SERVICES_MENU':
        # إرسال قائمة الخدمات
        send_services_menu(sender_id)
        
    elif payload.startswith('SERVICE_'):
        # تحديد الخدمة المطلوبة
        service = payload.replace('SERVICE_', '')
        
        # إرسال معلومات عن الخدمة
        if service == 'AI':
            response = "تقدم نيوفكر حلول الذكاء الاصطناعي المخصصة لتلبية احتياجات عملك. من روبوتات الدردشة الذكية إلى أنظمة التعلم الآلي، نحن نساعدك على الاستفادة من قوة الذكاء الاصطناعي."
        elif service == 'DIGITAL':
            response = "خدمات التحول الرقمي من نيوفكر تساعدك على تحديث عملياتك وتحسين كفاءة عملك. نحن نقدم حلول رقمية متكاملة تناسب احتياجاتك الفريدة."
        elif service == 'CONSULTING':
            response = "استشاراتنا المتخصصة في مجال التكنولوجيا والذكاء الاصطناعي تساعدك على اتخاذ القرارات الصحيحة لنمو عملك. فريقنا من الخبراء جاهز لمساعدتك."
        else:
            response = "نعتذر، لا توجد معلومات متاحة عن هذه الخدمة حالياً. يرجى التواصل مع فريق الدعم للحصول على مزيد من المعلومات."
            
        send_message(sender_id, response)
        
        # حفظ رد البوت في قاعدة البيانات
        save_conversation(sender_id, 'bot', response)
        
        # إضافة أزرار للإجراءات التالية
        buttons = [
            {
                "type": "postback",
                "title": "طلب هذه الخدمة",
                "payload": "ORDER_FORM"
            },
            {
                "type": "postback",
                "title": "خدمات أخرى",
                "payload": "SERVICES_MENU"
            }
        ]
        send_button_message(sender_id, "ماذا تريد أن تفعل بعد ذلك؟", buttons)

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
            elif "تصميم" في text.lower() or "واجهة" في text.lower():
                service_type = "تصميم واجهات"
            elif "تدريب" في text.lower() أو "استشارة" في text.lower():
                service_type = "تدريب واستشارات"
            elif "طلب" في text.lower() أو "عرض سعر" في text.lower() أو "خدمة" في text.lower():
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

<i>يمكنك إدارة هذا الطلب من خلال <a href="{BASE_DOMAIN}/orders">لوحة التحكم</a>.</i>
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
        {BASE_DOMAIN}/orders
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

def save_conversation(sender_id, sender_type, message):
    """
    Guarda un mensaje en el historial de conversaciones
    :param sender_id: ID del remitente (usuario de Facebook)
    :param sender_type: Tipo de remitente ('user' o 'bot')
    :param message: Texto del mensaje
    :return: None
    """
    try:
        # Buscar al cliente por su facebook_id
        customer = Customer.query.filter_by(facebook_id=sender_id).first()
        
        if not customer:
            # Si no existe el cliente, obtener información y guardarlo
            user_info = get_user_info(sender_id)
            customer = save_customer(sender_id, user_info)
            
            if not customer:
                print(f"No se pudo guardar la conversación: Cliente no encontrado para {sender_id}")
                return
        
        # Crear una nueva entrada en la conversación
        conversation = Conversation(
            customer_id=customer.id,  # Usar el ID del cliente de nuestra base de datos
            message=message,
            sender_type=sender_type,
            timestamp=datetime.now()
        )
        
        # Guardar en la base de datos
        db.session.add(conversation)
        db.session.commit()
        
        print(f"Conversación guardada para el cliente {customer.id} ({sender_type})")
    except Exception as e:
        print(f"Error al guardar la conversación: {str(e)}")
        db.session.rollback()

def send_customer_form(sender_id):
    """إرسال استمارة للحصول على معلومات العميل"""
    message_text = "يرجى ملء استمارة المعلومات التالية لتقديم الخدمة المطلوبة: https://example.com/form"
    send_message(sender_id, message_text)