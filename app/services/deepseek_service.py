import os
import requests
import json

# الحصول على إعدادات DeepSeek API من ملف .env
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'your_deepseek_api_key')
DEEPSEEK_API_URL = os.environ.get('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'deepseek-chat')
MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 200))
TEMPERATURE = float(os.environ.get('TEMPERATURE', 0.7))

def process_with_deepseek(text, user_info):
    """
    معالجة رسائل المستخدم باستخدام DeepSeek API
    
    Args:
        text (str): نص رسالة المستخدم
        user_info (dict): معلومات المستخدم من فيسبوك
        
    Returns:
        str: النص الناتج من DeepSeek للرد على المستخدم
    """
    try:
        # نظام البرومبت الذي يوجه الذكاء الاصطناعي للإجابة بشكل مناسب
        system_prompt = """
        أنت مساعد شركة NeoFikr Solutions للذكاء الاصطناعي والتحول الرقمي. قم بالرد على استفسارات العملاء بأسلوب ودي واحترافي.
        
        معلومات الشركة:
        - الاسم: NeoFikr Solutions
        - المجال: الذكاء الاصطناعي والتحول الرقمي
        - الخدمات: شات بوت، أنظمة CRM، تحليل بيانات، أتمتة عمليات، تصميم واجهات، تدريب واستشارات
        - رقم التواصل: 01121891913
        - البريد: neofikrsolutions@gmail.com
        - الموقع: https://neofikr.blogspot.com/
        
        باقات خدمات الشات بوت:
        - باقة Pro (Starter): 299 ج.م شهريًا - للشركات الصغيرة (حتى 1000 متابع)
        - باقة Business: 999 ج.م شهريًا - للشركات المتوسطة (حتى 5000 متابع)
        - باقة Growth: 2,500 ج.م شهريًا - للشركات النامية (حتى 15000 متابع)
        - باقة Enterprise: بدءًا من 6,000 ج.م شهريًا - للشركات الكبيرة (غير محدود)
        
        باقات خدمات CRM وتحليل البيانات:
        - حزمة Startup: 4,500 ج.م شهريًا
        - حزمة Growth: 9,800 ج.م شهريًا
        - حزمة Enterprise: 25,000 ج.م + شهريًا
        
        أسعار التدريب والاستشارات:
        - دورة تدريبية (8 ساعات): 1,500 ج.م للفرد
        - خطة دعم مميز (24/7): 1,200 ج.م / شهر
        
        عند طلب العميل معلومات عن الأسعار، قدم له التفاصيل واعرض عليه التحدث مع فريق المبيعات.
        إذا طلب العميل خدمة معينة، اطلب منه تفاصيل أكثر ووجهه للتواصل مع فريق المبيعات.
        حاول دائمًا الإجابة بإيجاز ووضوح، واحرص على الترحيب بالعميل وتقديم المساعدة.
        
        إذا كتب العميل رقمًا من 1 إلى 5، فهو يختار من القائمة الرئيسية:
        1 - خدمات الشركة
        2 - تحميل دليل أدوات الذكاء الاصطناعي
        3 - مشاهدة الكورسات والدورات
        4 - طلب استشارة أو عرض سعر
        5 - التحدث مع أحد أعضاء الفريق
        
        إذا كتب كلمة "قائمة" أو "menu" - اعرض القائمة الرئيسية
        """
        
        # إعداد الهيدرز للطلب
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # إعداد بيانات الطلب
        data = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS
        }
        
        # في حالة عدم توفر أو تكوين API، نستخدم الردود الثابتة للاختبار
        if DEEPSEEK_API_KEY == 'your_deepseek_api_key':
            print("استخدام وضع الاختبار (محاكاة API) للردود")
            return get_mock_response(text)
            
        # إرسال الطلب إلى DeepSeek API
        print(f"إرسال طلب إلى DeepSeek API: {DEEPSEEK_API_URL}")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            # استخراج النص المولد من استجابة API
            response_data = response.json()
            generated_text = response_data["choices"][0]["message"]["content"]
            print(f"تم استلام رد من DeepSeek API بنجاح ({len(generated_text)} حرف)")
            return generated_text
        else:
            print(f"خطأ في DeepSeek API: الرمز {response.status_code}")
            try:
                print(f"رسالة الخطأ: {response.json()}")
            except:
                print(f"نص الاستجابة الخام: {response.text}")
            return "عذرًا، حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى أو التواصل معنا مباشرة على 01121891913."
    
    except Exception as e:
        print(f"خطأ في طلب DeepSeek API: {e}")
        return get_mock_response(text)  # استخدام الردود الثابتة في حالة الخطأ

def get_mock_response(text):
    """
    الحصول على ردود ثابتة للاختبار في حالة عدم توفر API
    
    Args:
        text (str): نص رسالة المستخدم
        
    Returns:
        str: رد ثابت مناسب للرسالة
    """
    text_lower = text.lower()
    
    if "1" == text or "خدمات" in text_lower:
        return "خدمات الشركة نوفر مجموعة من الخدمات الذكية:\n🔹 تصميم شات بوت احترافي\n🔹 إنشاء CRM مخصص لإدارة العملاء\n🔹 أدوات تحليل بيانات ومراقبة الأداء\n🔹 أتمتة العمليات الرقمية\n🔹 تصميم واجهات ذكية للتطبيقات\n🔹 استشارات وتدريب في الذكاء الاصطناعي\n\nاكتب رقم الخدمة لمزيد من التفاصيل."
    
    elif "2" == text or "دليل" in text_lower:
        return "تحميل الدليل المجاني 📘 إليك دليلنا العملي:\n\"أقوى 10 أدوات ذكاء اصطناعي تساعدك في إدارة مشروعك\"\n📥 رابط التحميل: https://neofikr.blogspot.com/ai-tools-guide"
    
    elif "3" == text or "كورس" in text_lower or "دورة" in text_lower:
        return "مشاهدة الكورسات 📚 الدورات المتاحة حاليًا:\n\n▪️ دورة: كيف تبدأ مشروعك باستخدام أدوات AI\n▪️ ورشة: إنشاء شات بوت لعملك خلال 60 دقيقة\n▪️ تدريب عملي على أدوات Canva AI وChatGPT\n\n🟢 للتسجيل أو مشاهدة التفاصيل، اضغط هنا: https://neofikr.blogspot.com/courses"
    
    elif "4" == text or "استشارة" in text_lower:
        return "طلب استشارة من فضلك أرسل لنا:\n\n▪️ اسمك الكامل\n▪️ طبيعة مشروعك\n▪️ ما الذي تحتاج إليه (شات بوت؟ CRM؟ تدريب؟)\n\nوسيتم الرد عليك خلال 24 ساعة من فريقنا المتخصص."
    
    elif "5" == text or "تواصل" in text_lower:
        return "سيتم تحويلك الآن إلى أحد أعضاء الفريق عبر الواتساب.\n📞 01121891913"
    
    elif "سعر" in text_lower or "تكلفة" in text_lower or "أسعار" in text_lower:
        return "باقات الخدمات لدينا:\n\n" + \
               "▪️ باقة Pro (Starter): 299 ج.م شهريًا - للشركات الصغيرة\n" + \
               "▪️ باقة Business: 999 ج.م شهريًا - للشركات المتوسطة\n" + \
               "▪️ باقة Growth: 2,500 ج.م شهريًا - للشركات النامية\n" + \
               "▪️ باقة Enterprise: بدءًا من 6,000 ج.م شهريًا - للشركات الكبيرة\n\n" + \
               "هل ترغب في التحدث مع أحد أعضاء فريق المبيعات للحصول على عرض مخصص؟"
    
    elif "طلب" in text_lower or "خدمة" in text_lower or "اطلب" in text_lower:
        return "شكرًا لاهتمامك بخدماتنا! لنقدم لك أفضل حل، نحتاج إلى بعض المعلومات:\n\n" + \
               "▪️ ما هو مجال عملك؟\n" + \
               "▪️ ما هي الخدمة التي تهتم بها تحديدًا؟\n" + \
               "▪️ هل لديك موعد محدد تحتاج فيه إطلاق المشروع؟\n\n" + \
               "سيقوم فريقنا بالتواصل معك قريبًا على الرقم المسجل لديك."
    
    elif "شات بوت" in text_lower or "chatbot" in text_lower:
        return "خدمة الشات بوت 🤖 من NeoFikr تمنحك:\n\n" + \
               "✅ بوت ذكي يرد على كل استفسارات عملائك\n" + \
               "✅ جمع بيانات العملاء وتحويلهم لمبيعات\n" + \
               "✅ ربط مع فيسبوك أو واتساب أو موقعك\n" + \
               "✅ يعمل 24/7 بدون توقف\n\n" + \
               "أسعارنا تبدأ من 299 ج.م شهريًا. هل ترغب في معرفة المزيد؟"
    
    elif "قائمة" in text_lower or "menu" in text_lower:
        return "القائمة الرئيسية 📋\n\n" + \
               "1️⃣ خدمات الشركة\n" + \
               "2️⃣ تحميل دليل أدوات الذكاء الاصطناعي\n" + \
               "3️⃣ مشاهدة الكورسات والدورات\n" + \
               "4️⃣ طلب استشارة أو عرض سعر\n" + \
               "5️⃣ التحدث مع أحد أعضاء الفريق\n\n" + \
               "اختر رقم الخدمة أو اكتب استفسارك وسأساعدك."
    
    else:
        return "شكرًا لتواصلك مع NeoFikr Solutions! يمكنك اختيار من القائمة التالية:\n\n" + \
               "1️⃣ خدمات الشركة\n" + \
               "2️⃣ تحميل دليل أدوات الذكاء الاصطناعي\n" + \
               "3️⃣ مشاهدة الكورسات والدورات\n" + \
               "4️⃣ طلب استشارة أو عرض سعر\n" + \
               "5️⃣ التحدث مع أحد أعضاء الفريق\n\n" + \
               "أو يمكنك كتابة استفسارك وسأحاول مساعدتك."