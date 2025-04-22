from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
from app import db
from app.models.customer import Customer
from app.models.order import Order
from datetime import datetime, timedelta
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# اسم المستخدم وكلمة المرور للوصول للوحة التحكم
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'neofikr2025')

# دالة للتحقق من تسجيل الدخول
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول للوحة التحكم"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            error = 'بيانات غير صحيحة. يرجى المحاولة مرة أخرى.'
    
    return render_template('admin/login.html', error=error)

@admin_bp.route('/logout')
def logout():
    """تسجيل الخروج من لوحة التحكم"""
    session.pop('logged_in', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """الصفحة الرئيسية للوحة التحكم"""
    # إحصائيات عامة
    total_customers = Customer.query.count()
    total_orders = Order.query.count()
    new_orders = Order.query.filter_by(status='جديد').count()
    
    # آخر 5 طلبات
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # إحصائيات الطلبات حسب الحالة
    status_stats = db.session.query(
        Order.status, 
        db.func.count(Order.id)
    ).group_by(Order.status).all()
    
    return render_template('admin/dashboard.html',
                          total_customers=total_customers,
                          total_orders=total_orders,
                          new_orders=new_orders,
                          recent_orders=recent_orders,
                          status_stats=status_stats)

@admin_bp.route('/orders')
@login_required
def orders():
    """عرض جميع الطلبات"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', None)
    
    query = Order.query
    
    # تطبيق الفلتر حسب الحالة إذا تم تحديده
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # ترتيب الطلبات من الأحدث للأقدم
    orders_pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('admin/orders.html', 
                          orders=orders_pagination.items, 
                          pagination=orders_pagination,
                          status_filter=status_filter)

@admin_bp.route('/orders/<int:order_id>')
@login_required
def order_details(order_id):
    """عرض تفاصيل طلب محدد"""
    order = Order.query.get_or_404(order_id)
    customer = Customer.query.get(order.customer_id)
    
    return render_template('admin/order_details.html', order=order, customer=customer)

@admin_bp.route('/orders/<int:order_id>/update', methods=['POST'])
@login_required
def update_order(order_id):
    """تحديث حالة طلب معين"""
    order = Order.query.get_or_404(order_id)
    
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    if status:
        order.status = status
    if notes:
        order.details += f"\n\n--- ملاحظات الإدارة ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n{notes}"
    
    db.session.commit()
    
    return redirect(url_for('admin.order_details', order_id=order_id))

@admin_bp.route('/customers')
@login_required
def customers():
    """عرض قائمة العملاء"""
    page = request.args.get('page', 1, type=int)
    customers_pagination = Customer.query.order_by(Customer.created_at.desc()).paginate(page=page, per_page=15)
    
    return render_template('admin/customers.html', 
                          customers=customers_pagination.items, 
                          pagination=customers_pagination)

@admin_bp.route('/customers/<int:customer_id>')
@login_required
def customer_details(customer_id):
    """عرض تفاصيل عميل معين وطلباته"""
    customer = Customer.query.get_or_404(customer_id)
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    
    return render_template('admin/customer_details.html', customer=customer, orders=orders)

@admin_bp.route('/reports')
@login_required
def reports():
    """عرض تقارير وإحصائيات"""
    # الحصول على الفترة المطلوبة من معلمات URL
    period = request.args.get('period', 'week')
    
    # تحديد الفترة الزمنية
    end_date = datetime.now()
    
    if period == 'day':
        start_date = end_date - timedelta(days=1)
        period_text = 'اليوم'
        date_format = '%H:%M'  # ساعات
    elif period == 'week':
        start_date = end_date - timedelta(days=7)
        period_text = 'آخر أسبوع'
        date_format = '%m-%d'  # شهر-يوم
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
        period_text = 'آخر شهر'
        date_format = '%m-%d'  # شهر-يوم
    elif period == 'year':
        start_date = end_date - timedelta(days=365)
        period_text = 'هذا العام'
        date_format = '%m-%Y'  # شهر-سنة
    else:  # 'all'
        start_date = datetime(2020, 1, 1)  # تاريخ قديم كافي لكل البيانات
        period_text = 'كل الفترات'
        date_format = '%m-%Y'  # شهر-سنة
    
    # إحصائيات عامة
    total_orders = Order.query.filter(Order.created_at >= start_date).count()
    new_customers = Customer.query.filter(Customer.created_at >= start_date).count()
    
    # معدل التفاعل والاكتمال (نسبة مئوية)
    # هذا مجرد مثال - يمكن تعديله حسب حساباتك الفعلية
    completed_orders = Order.query.filter(Order.status == 'مكتمل', Order.created_at >= start_date).count()
    completion_rate = int((completed_orders / total_orders * 100) if total_orders > 0 else 0)
    engagement_rate = int((total_orders / new_customers * 50) if new_customers > 0 else 0)
    if engagement_rate > 100:
        engagement_rate = 100
    
    # بيانات الرسم البياني للطلبات
    if period == 'day':
        # إحصائيات بالساعة لليوم الواحد
        timeline_data = db.session.query(
            db.func.strftime('%H:00', Order.created_at),
            db.func.count(Order.id)
        ).filter(
            Order.created_at >= start_date
        ).group_by(
            db.func.strftime('%H', Order.created_at)
        ).all()
    elif period in ['week', 'month']:
        # إحصائيات يومية لفترة أسبوع أو شهر
        timeline_data = db.session.query(
            db.func.date(Order.created_at),
            db.func.count(Order.id)
        ).filter(
            Order.created_at >= start_date
        ).group_by(
            db.func.date(Order.created_at)
        ).all()
    else:
        # إحصائيات شهرية للسنة أو كل الفترات
        timeline_data = db.session.query(
            db.func.strftime('%Y-%m', Order.created_at),
            db.func.count(Order.id)
        ).filter(
            Order.created_at >= start_date
        ).group_by(
            db.func.strftime('%Y-%m', Order.created_at)
        ).all()
    
    # تحويل البيانات إلى تنسيق مناسب للرسم البياني
    timeline_labels = []
    orders_data = []
    
    if timeline_data:
        for date_str, count in timeline_data:
            if isinstance(date_str, str):
                # إذا كان التاريخ عبارة عن سلسلة
                timeline_labels.append(date_str)
            else:
                # إذا كان التاريخ من نوع datetime.date
                formatted_date = date_str.strftime(date_format)
                timeline_labels.append(formatted_date)
            orders_data.append(count)
    else:
        # إذا لم تكن هناك بيانات، أضف قيمة افتراضية
        timeline_labels = ["لا توجد بيانات"]
        orders_data = [0]
    
    # إحصائيات حسب حالة الطلب
    status_data_query = db.session.query(
        Order.status,
        db.func.count(Order.id)
    ).filter(
        Order.created_at >= start_date
    ).group_by(Order.status).all()
    
    # تحويل بيانات الحالة إلى تنسيق مناسب للرسم البياني
    status_labels = []
    status_data = []
    
    if status_data_query:
        for status, count in status_data_query:
            status_labels.append(status or "غير محدد")
            status_data.append(count)
    else:
        # إذا لم تكن هناك بيانات، أضف قيمة افتراضية
        status_labels = ["لا توجد بيانات"]
        status_data = [0]
    
    # إحصائيات حسب نوع الخدمة
    service_stats = db.session.query(
        Order.service_type,
        db.func.count(Order.id)
    ).filter(
        Order.created_at >= start_date
    ).group_by(Order.service_type).all()
    
    # العملاء الأكثر نشاطاً
    top_customers_query = db.session.query(Customer).join(Order, Customer.id == Order.customer_id).filter(
        Order.created_at >= start_date
    ).group_by(Customer.id).order_by(db.func.count(Order.id).desc()).limit(5).all()
    
    # إضافة آخر تفاعل لكل عميل
    top_customers = []
    for customer in top_customers_query:
        last_order = Order.query.filter_by(customer_id=customer.id).order_by(Order.created_at.desc()).first()
        if last_order:
            customer.last_interaction = last_order.created_at
            top_customers.append(customer)
    
    return render_template('admin/reports.html',
                          period=period,
                          period_text=period_text,
                          total_orders=total_orders,
                          new_customers=new_customers,
                          engagement_rate=engagement_rate,
                          completion_rate=completion_rate,
                          timeline_labels=timeline_labels,
                          orders_data=orders_data,
                          status_labels=status_labels,
                          status_data=status_data,
                          service_stats=service_stats,
                          top_customers=top_customers)

@admin_bp.route('/api/update-order-status', methods=['POST'])
@login_required
def api_update_order_status():
    """API لتحديث حالة الطلب بدون تحديث الصفحة"""
    if not request.is_json:
        return jsonify({'error': 'يجب إرسال طلب JSON'}), 400
    
    data = request.get_json()
    order_id = data.get('order_id')
    status = data.get('status')
    
    if not order_id or not status:
        return jsonify({'error': 'يجب تحديد معرف الطلب والحالة الجديدة'}), 400
    
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'الطلب غير موجود'}), 404
        
        order.status = status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'تم تحديث حالة الطلب إلى {status}',
            'status': status,
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

@admin_bp.route('/export-report')
@login_required
def export_report():
    """تصدير البيانات إلى تقرير بصيغة Excel أو PDF أو CSV"""
    period = request.args.get('period', 'all')
    report_type = request.args.get('type', 'all')
    report_format = request.args.get('format', 'excel')
    
    # تحديد الفترة الزمنية
    end_date = datetime.now()
    if period == 'day':
        start_date = end_date - timedelta(days=1)
        period_str = 'اليوم'
    elif period == 'week':
        start_date = end_date - timedelta(days=7)
        period_str = 'آخر أسبوع'
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
        period_str = 'آخر شهر'
    elif period == 'year':
        start_date = end_date - timedelta(days=365)
        period_str = 'هذا العام'
    else:  # 'all'
        start_date = datetime(2020, 1, 1)
        period_str = 'كل الفترات'
    
    # سيتم توسيعها لاحقاً لإنشاء ملفات Excel وPDF وCSV حقيقية
    # بالنسبة للآن، نعرض البيانات في الصفحة
    
    if report_type == 'orders' or report_type == 'all':
        orders = Order.query.filter(Order.created_at >= start_date).order_by(Order.created_at.desc()).all()
    else:
        orders = []
    
    if report_type == 'customers' or report_type == 'all':
        customers = Customer.query.filter(Customer.created_at >= start_date).order_by(Customer.created_at.desc()).all()
    else:
        customers = []
    
    if report_type == 'services' or report_type == 'all':
        services = db.session.query(
            Order.service_type,
            db.func.count(Order.id)
        ).filter(
            Order.created_at >= start_date
        ).group_by(Order.service_type).all()
    else:
        services = []
    
    # عرض صفحة مؤقتة تحتوي على البيانات بدلاً من التصدير الفعلي للآن
    return render_template('admin/export_report.html',
                          period=period_str,
                          report_type=report_type,
                          report_format=report_format,
                          orders=orders,
                          customers=customers,
                          services=services,
                          start_date=start_date,
                          end_date=end_date)