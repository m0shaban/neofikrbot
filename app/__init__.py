from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# تهيئة قاعدة البيانات
db = SQLAlchemy()

def create_app():
    # إنشاء وتكوين التطبيق
    app = Flask(__name__)
    
    # تكوين قاعدة البيانات
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///chatbot.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # إضافة متغير للدومين الحالي
    app.config['BASE_URL'] = os.environ.get('BASE_URL', 'https://neofikrbot.onrender.com')
    
    # ربط قاعدة البيانات مع التطبيق
    db.init_app(app)
    
    # تسجيل النماذج الأساسية
    from app.models.customer import Customer
    from app.models.order import Order
    
    # تسجيل مسارات API
    from app.controllers.webhook_controller import webhook_bp
    from app.controllers.admin_controller import admin_bp
    
    app.register_blueprint(webhook_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app