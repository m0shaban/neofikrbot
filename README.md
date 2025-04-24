# NeoFikr Solutions - منصة ذكاء اصطناعي للخدمة العملاء

<div dir="rtl">

## نظرة عامة

تطبيق NeoFikr Solutions هو منصة متكاملة للذكاء الاصطناعي تعمل كواجهة لخدمة العملاء عبر القنوات المتعددة مثل فيسبوك ماسنجر وتيليجرام. يتضمن التطبيق لوحة تحكم إدارية متقدمة تتيح للمسؤولين إدارة الطلبات والعملاء ومراقبة أداء النظام بشكل فعال.

## المميزات الرئيسية

### روبوت دردشة ذكي
- تكامل مع منصة DeepSeek للذكاء الاصطناعي
- دعم المحادثات الطبيعية والتفاعلية
- إمكانية التخصيص وفقًا لاحتياجات العمل
- حفظ سجلات المحادثات لتحليلها لاحقًا

### قنوات متعددة
- تكامل مع فيسبوك ماسنجر
- دعم تيليجرام 
- إمكانية التوسع لدعم واتساب

### لوحة تحكم إدارية
- واجهة سهلة الاستخدام للمسؤولين
- إدارة قاعدة بيانات العملاء
- عرض وإدارة الطلبات
- تقارير وإحصائيات مفصلة
- تصدير التقارير بصيغ مختلفة

### نظام الإشعارات
- إشعارات عبر البريد الإلكتروني
- إشعارات عبر تيليجرام
- دعم إشعارات واتساب (قيد الإعداد)

## المتطلبات التقنية

- Python 3.8 أو أحدث
- Flask 2.0.1
- Flask-SQLAlchemy 2.5.1
- SQLAlchemy 1.4.23
- python-dotenv 0.19.0
- requests 2.26.0
- gunicorn 20.1.0 (للنشر)
- Werkzeug 2.0.1
- Jinja2 3.0.1
- email-validator 1.1.3
- pymysql 1.0.2 (للتوافق مع قواعد بيانات MySQL)

## هيكل المشروع

```
/
├── app/                      # الحزمة الرئيسية للتطبيق
│   ├── __init__.py           # إعداد التطبيق وتهيئته
│   ├── controllers/          # وحدات التحكم بالمسارات
│   │   ├── admin_controller.py  # مسارات لوحة التحكم الإدارية
│   │   └── webhook_controller.py # معالجة webhooks
│   ├── models/               # نماذج قاعدة البيانات
│   │   ├── conversation.py   # نموذج المحادثات
│   │   ├── customer.py       # نموذج العملاء
│   │   └── order.py          # نموذج الطلبات
│   ├── services/             # خدمات التطبيق
│   │   ├── deepseek_service.py     # خدمة الذكاء الاصطناعي
│   │   └── notification_service.py # خدمة الإشعارات
│   ├── static/               # الملفات الثابتة (CSS، JS، الصور)
│   ├── templates/            # قوالب HTML
│   │   └── admin/            # قوالب لوحة التحكم
│   └── utils/                # أدوات مساعدة
├── config/                   # ملفات الإعدادات
├── docs/                     # وثائق المشروع
├── logs/                     # ملفات السجلات
├── migrations/               # ملفات ترحيل قاعدة البيانات
├── tests/                    # اختبارات الوحدة والتكامل
├── .env                      # ملف متغيرات البيئة
├── Procfile                  # ملف Procfile للنشر
├── README.md                 # هذا الملف
├── requirements.txt          # متطلبات بيئة Python
├── run.py                    # نقطة بدء التشغيل
└── wsgi.py                   # نقطة دخول لخادم WSGI
```

## طريقة التثبيت والإعداد

### 1. استنساخ المشروع:
```bash
git clone https://github.com/yourusername/neofikr-solutions.git
cd neofikr-solutions
```

### 2. إنشاء بيئة افتراضية وتفعيلها:
```bash
python -m venv venv
# لنظام Linux/Mac
source venv/bin/activate
# لنظام Windows
venv\Scripts\activate
```

### 3. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

### 4. إعداد ملف البيئة:
قم بإنشاء ملف `.env` في المجلد الرئيسي للمشروع وأضف المتغيرات التالية:

```
# تكوين التطبيق
SECRET_KEY=your_secret_key
DEBUG=True
BASE_URL=https://yourapp.com

# قاعدة البيانات
DATABASE_URI=sqlite:///chatbot.db

# Facebook
VERIFY_TOKEN=your_facebook_webhook_verify_token
PAGE_ACCESS_TOKEN=your_facebook_page_access_token

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEFAULT_MODEL=deepseek-chat
MAX_TOKENS=200
TEMPERATURE=0.7

# إعدادات البريد الإلكتروني
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# إعدادات تيليجرام
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# معلومات المدير
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password
```

### 5. تهيئة قاعدة البيانات:
```bash
python run.py
```

### 6. تشغيل التطبيق للتطوير:
```bash
flask run
```

## إعداد Webhook لفيسبوك ماسنجر

1. أنشئ صفحة على فيسبوك وتطبيق فيسبوك من خلال [مركز مطوري فيسبوك](https://developers.facebook.com/).
2. أضف منتج Messenger إلى تطبيقك.
3. قم بتوليد رمز وصول دائم للصفحة (PAGE_ACCESS_TOKEN) وأضفه إلى ملف `.env`.
4. قم بإعداد webhook مع عنوان URL الخاص بتطبيقك:
   ```
   https://your-app-domain.com/webhook
   ```
5. استخدم رمز التحقق (VERIFY_TOKEN) الذي حددته في ملف `.env`.
6. اختر الأحداث التي ترغب في الاشتراك فيها (`messages`, `messaging_postbacks`).

## إعداد تيليجرام

1. أنشئ بوت على تيليجرام باستخدام [BotFather](https://t.me/botfather).
2. احصل على رمز الوصول الخاص بالبوت (TELEGRAM_BOT_TOKEN).
3. ابدأ محادثة مع البوت وابحث عن معرف الدردشة (CHAT_ID).
4. أضف هذه المعلومات إلى ملف `.env`.

## النشر على سيرفر الإنتاج

### النشر على Render.com

1. أنشئ حسابًا على [Render.com](https://render.com).
2. قم بربط حسابك على Render بمستودع GitHub الخاص بك.
3. أنشئ تطبيق ويب جديد واختر المستودع الخاص بالمشروع.
4. قم بتعيين النوع إلى Python وأضف أمر البدء:
   ```
   gunicorn wsgi:app
   ```
5. أضف جميع متغيرات البيئة من ملف `.env` إلى إعدادات البيئة في Render.
6. انقر على "Create Web Service" وانتظر اكتمال عملية النشر.

عنوان webhook لفيسبوك سيكون:
```
https://your-app-name.onrender.com/webhook
```

### النشر على Heroku

1. قم بتثبيت [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).
2. قم بتسجيل الدخول إلى حسابك:
   ```bash
   heroku login
   ```
3. أنشئ تطبيق Heroku:
   ```bash
   heroku create your-app-name
   ```
4. أضف متغيرات البيئة:
   ```bash
   heroku config:set SECRET_KEY=your_secret_key
   # قم بإضافة باقي المتغيرات
   ```
5. نشر التطبيق:
   ```bash
   git push heroku main
   ```

## لوحة التحكم الإدارية

يمكن الوصول إلى لوحة التحكم الإدارية من خلال المسار `/admin`:
```
https://your-app-domain.com/admin
```

استخدم اسم المستخدم وكلمة المرور المحددين في ملف `.env` لتسجيل الدخول.

## الميزات المستقبلية

- دعم واتساب
- تحسين واجهة المستخدم للوحة التحكم
- تحليلات متقدمة للمحادثات
- دعم لغات إضافية
- تكامل مع أنظمة CRM

## المساهمة في المشروع

نرحب بالمساهمات من المطورين! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'إضافة ميزة رائعة'`)
4. Push إلى الفرع (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## الترخيص

تم تطوير هذا المشروع بواسطة NeoFikr Solutions. جميع الحقوق محفوظة © 2025.

## الدعم والتواصل

للدعم الفني أو الاستفسارات، يرجى التواصل عبر:

- البريد الإلكتروني: neofikrsolutions@gmail.com
- الموقع الإلكتروني: [www.neofikrsolutions.com](https://www.neofikrsolutions.com)

</div>