from dotenv import load_dotenv
import sys
import os

# تحميل متغيرات البيئة
load_dotenv()

# إضافة مسار المشروع للـ PYTHONPATH
sys.path.append(os.path.abspath('.'))

# استيراد خدمة DeepSeek
from app.services.deepseek_service import process_with_deepseek

def test_deepseek():
    """
    اختبار خدمة DeepSeek API بشكل مباشر
    """
    print("==== اختبار خدمة DeepSeek API ====")
    print("(اكتب 'خروج' للخروج)\n")
    
    user_info = {
        "first_name": "مستخدم",
        "last_name": "اختبار"
    }
    
    while True:
        user_input = input("\nأدخل سؤالك: ")
        
        if user_input.lower() in ['خروج', 'exit', 'quit']:
            print("شكرًا لاستخدام اختبار خدمة DeepSeek API")
            break
            
        print("\nجاري معالجة السؤال...")
        response = process_with_deepseek(user_input, user_info)
        print("\n=== الرد ===\n")
        print(response)
        print("\n============")

if __name__ == "__main__":
    test_deepseek()