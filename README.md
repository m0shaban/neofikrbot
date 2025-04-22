# نظام شات بوت NeoFikr Solutions

نظام شات بوت متكامل لشركة NeoFikr Solutions مع واجهة إدارة كاملة لمتابعة الطلبات والعملاء، مع إمكانية الربط مع فيسبوك ماسنجر واستخدام DeepSeek API للذكاء الاصطناعي.

## المميزات

- شات بوت ذكي مع ردود آلية باستخدام DeepSeek API
- واجهة إدارية متكاملة لمتابعة وإدارة الطلبات
- نظام إشعارات عبر البريد الإلكتروني والواتساب
- قاعدة بيانات لتخزين العملاء والطلبات
- دعم كامل للغة العربية
- إحصائيات وتقارير حول النشاط

## متطلبات التشغيل

- Python 3.8+
- Flask 2.0+
- SQLAlchemy
- قاعدة بيانات (SQLite للتطوير، PostgreSQL/MySQL للإنتاج)
- حساب مطوّر على فيسبوك
- حساب DeepSeek API (للذكاء الاصطناعي)
- اختياري: حساب واتساب بزنس API

## خطوات الإعداد

### 1. تجهيز البيئة الافتراضية

```bash
# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة الافتراضية (Windows)
venv\Scripts\activate

# تفعيل البيئة الافتراضية (Linux/macOS)
source venv/bin/activate
```

### 2. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements.txt
```

### 3. إعداد متغيرات البيئة

قم بإنشاء نسخة من ملف `.env.example` باسم `.env` وتعبئة القيم المناسبة:

```
# تكوين التطبيق
SECRET_KEY=your_secret_key
DEBUG=True

# قاعدة البيانات
DATABASE_URI=sqlite:///chatbot.db

# Facebook
VERIFY_TOKEN=your_facebook_webhook_verify_token
PAGE_ACCESS_TOKEN=your_facebook_page_access_token

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key

# إعدادات البريد الإلكتروني
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# إعدادات واتساب
WHATSAPP_API_KEY=your_whatsapp_api_key
WHATSAPP_PHONE_ID=your_whatsapp_phone_number_id

# معلومات المدير
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

### 4. إعداد قاعدة البيانات

قاعدة البيانات ستنشأ تلقائيًا عند تشغيل التطبيق لأول مرة. إذا كنت ترغب في استخدام قاعدة بيانات PostgreSQL أو MySQL، قم بتحديث متغير `DATABASE_URI` بشكل مناسب.

### 5. تشغيل التطبيق

```bash
# للتطوير
python run.py

# للإنتاج باستخدام gunicorn
gunicorn -w 4 "run:app" --bind 0.0.0.0:5000
```

### 6. إعداد Webhook فيسبوك

1. قم بإنشاء تطبيق فيسبوك وصفحة على [Facebook Developer Portal](https://developers.facebook.com/)
2. قم بإعداد Webhook للرسائل، واستخدم `your_domain/webhook` كعنوان Callback URL
3. أدخل نفس قيمة `VERIFY_TOKEN` التي قمت بتخزينها في ملف `.env`
4. تأكد من اشتراك التطبيق في أحداث `messages` و `messaging_postbacks`

## الوصول للوحة التحكم

بعد تشغيل التطبيق، يمكن الوصول للوحة التحكم من خلال:

```
http://your_domain/admin/login
```

استخدم بيانات الدخول التي قمت بتعيينها في ملف `.env`:

- اسم المستخدم: ADMIN_USERNAME
- كلمة المرور: ADMIN_PASSWORD

## الهيكل العام للمشروع

```
├── app/                    # المجلد الرئيسي للتطبيق
│   ├── __init__.py         # تهيئة التطبيق
│   ├── controllers/        # متحكمات المسارات
│   │   ├── admin_controller.py  # متحكم لوحة الإدارة
│   │   └── webhook_controller.py # متحكم webhook لفيسبوك
│   ├── models/             # نماذج قاعدة البيانات
│   │   ├── customer.py     # نموذج العميل
│   │   └── order.py        # نموذج الطلب
│   ├── services/           # خدمات التطبيق
│   │   ├── deepseek_service.py   # خدمة الذكاء الاصطناعي
│   │   └── notification_service.py # خدمة الإشعارات
│   ├── static/             # الملفات الثابتة (CSS, JS)
│   ├── templates/          # قوالب HTML
│   │   └── admin/          # قوالب لوحة الإدارة
│   └── utils/              # أدوات مساعدة
├── config/                 # ملفات التكوين
├── docs/                   # الوثائق
├── logs/                   # ملفات السجلات
├── migrations/             # ترقيات قاعدة البيانات
├── tests/                  # اختبارات
├── .env                    # متغيرات البيئة
├── .env.example            # نموذج لمتغيرات البيئة
├── .gitignore              # ملفات مستثناة من git
├── requirements.txt        # متطلبات Python
├── run.py                  # نقطة بدء التطبيق
└── README.md               # توثيق المشروع
```

## الدعم الفني

للمساعدة أو الاستفسارات، يرجى التواصل مع:

- البريد الإلكتروني: neofikrsolutions@gmail.com
- الواتساب: 01121891913
- الموقع: https://neofikr.blogspot.com/