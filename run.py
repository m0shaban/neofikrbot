from app import create_app, db
import os

app = create_app()

# إنشاء قاعدة البيانات عند تشغيل التطبيق
@app.before_first_request
def initialize_database():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)