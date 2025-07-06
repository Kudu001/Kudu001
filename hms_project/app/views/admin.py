from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.billing import Bill, Payment
from app.models.inventory import InventoryItem
from datetime import date, datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_access_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard."""
    today = date.today()
    
    # Basic statistics
    total_patients = Patient.query.filter(Patient.is_active == True).count()
    total_staff = Staff.query.filter(Staff.is_active == True).count()
    today_appointments = Appointment.query.filter(
        func.date(Appointment.appointment_date) == today
    ).count()
    total_revenue = db.session.query(func.sum(Payment.amount)).scalar() or 0
    
    # Recent activities
    recent_patients = Patient.query.filter(Patient.is_active == True).order_by(
        Patient.created_at.desc()
    ).limit(5).all()
    
    recent_appointments = Appointment.query.filter(
        Appointment.appointment_date >= today
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(5).all()
    
    # Low stock items
    low_stock_items = InventoryItem.query.filter(
        InventoryItem.current_stock <= InventoryItem.minimum_stock,
        InventoryItem.is_active == True
    ).limit(5).all()
    
    # Monthly revenue data for chart
    monthly_revenue = []
    for i in range(12):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end - timedelta(days=month_end.day)
        
        revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= month_start,
            Payment.payment_date <= month_end
        ).scalar() or 0
        
        monthly_revenue.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(revenue)
        })
    
    monthly_revenue.reverse()
    
    return render_template('admin/dashboard.html',
                         total_patients=total_patients,
                         total_staff=total_staff,
                         today_appointments=today_appointments,
                         total_revenue=total_revenue,
                         recent_patients=recent_patients,
                         recent_appointments=recent_appointments,
                         low_stock_items=low_stock_items,
                         monthly_revenue=monthly_revenue)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users."""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create new user."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Validation
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('admin/create_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('admin/create_user.html')
        
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {username} created successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html')

@admin_bp.route('/users/<int:user_id>/toggle_active')
@login_required
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status."""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} {status} successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/patients')
@login_required
@admin_required
def patients():
    """Manage patients."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Patient.query.filter(Patient.is_active == True)
    
    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.patient_id.ilike(f'%{search}%'),
                Patient.phone.ilike(f'%{search}%')
            )
        )
    
    patients = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/patients.html', patients=patients, search=search)

@admin_bp.route('/staff')
@login_required
@admin_required
def staff():
    """Manage staff."""
    page = request.args.get('page', 1, type=int)
    department = request.args.get('department', '')
    
    query = Staff.query.filter(Staff.is_active == True)
    
    if department:
        query = query.filter(Staff.department == department)
    
    staff_members = query.order_by(Staff.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    departments = db.session.query(Staff.department).distinct().all()
    departments = [d[0] for d in departments]
    
    return render_template('admin/staff.html', 
                         staff_members=staff_members, 
                         departments=departments,
                         selected_department=department)

@admin_bp.route('/staff/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_staff():
    """Create new staff member."""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        email = request.form.get('email')
        department = request.form.get('department')
        specialization = request.form.get('specialization')
        qualification = request.form.get('qualification')
        
        staff = Staff(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            phone=phone,
            email=email,
            department=department,
            specialization=specialization,
            qualification=qualification
        )
        
        db.session.add(staff)
        db.session.commit()
        
        flash(f'Staff member {staff.full_name} created successfully.', 'success')
        return redirect(url_for('admin.staff'))
    
    return render_template('admin/create_staff.html')

@admin_bp.route('/appointments')
@login_required
@admin_required
def appointments():
    """Manage appointments."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    
    query = Appointment.query
    
    if status:
        query = query.filter(Appointment.status == status)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(func.date(Appointment.appointment_date) == filter_date)
        except ValueError:
            pass
    
    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/appointments.html', 
                         appointments=appointments,
                         selected_status=status,
                         selected_date=date_filter)

@admin_bp.route('/billing')
@login_required
@admin_required
def billing():
    """Manage billing."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Bill.query
    
    if status:
        query = query.filter(Bill.status == status)
    
    bills = query.order_by(Bill.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Calculate summary statistics
    total_amount = db.session.query(func.sum(Bill.total_amount)).scalar() or 0
    paid_amount = db.session.query(func.sum(Bill.paid_amount)).scalar() or 0
    outstanding = total_amount - paid_amount
    
    return render_template('admin/billing.html',
                         bills=bills,
                         selected_status=status,
                         total_amount=total_amount,
                         paid_amount=paid_amount,
                         outstanding=outstanding)

@admin_bp.route('/inventory')
@login_required
@admin_required
def inventory():
    """Manage inventory."""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    low_stock = request.args.get('low_stock', False, type=bool)
    
    query = InventoryItem.query.filter(InventoryItem.is_active == True)
    
    if category:
        query = query.filter(InventoryItem.category == category)
    
    if low_stock:
        query = query.filter(InventoryItem.current_stock <= InventoryItem.minimum_stock)
    
    items = query.order_by(InventoryItem.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = ['Medicine', 'Equipment', 'Supplies', 'Consumables']
    
    return render_template('admin/inventory.html',
                         items=items,
                         categories=categories,
                         selected_category=category,
                         low_stock_filter=low_stock)

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """System reports."""
    # Patient statistics
    total_patients = Patient.query.filter(Patient.is_active == True).count()
    new_patients_this_month = Patient.query.filter(
        Patient.created_at >= date.today().replace(day=1)
    ).count()
    
    # Appointment statistics
    total_appointments = Appointment.query.count()
    completed_appointments = Appointment.query.filter(
        Appointment.status == 'completed'
    ).count()
    
    # Revenue statistics
    total_revenue = db.session.query(func.sum(Payment.amount)).scalar() or 0
    this_month_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.payment_date >= date.today().replace(day=1)
    ).scalar() or 0
    
    # Staff statistics
    staff_by_department = db.session.query(
        Staff.department, func.count(Staff.id)
    ).filter(Staff.is_active == True).group_by(Staff.department).all()
    
    return render_template('admin/reports.html',
                         total_patients=total_patients,
                         new_patients_this_month=new_patients_this_month,
                         total_appointments=total_appointments,
                         completed_appointments=completed_appointments,
                         total_revenue=total_revenue,
                         this_month_revenue=this_month_revenue,
                         staff_by_department=staff_by_department)

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """System settings."""
    return render_template('admin/settings.html')