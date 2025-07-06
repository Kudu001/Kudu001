from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.staff import Staff, AttendanceRecord
from app.models.billing import Bill, Payment
from app.models.inventory import InventoryItem
from datetime import date, datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin role."""
    def decorated_function(*args, **kwargs):
        if not current_user.can_access_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview."""
    today = date.today()
    
    # Get basic statistics
    stats = {
        'total_patients': Patient.query.filter(Patient.is_active == True).count(),
        'total_staff': Staff.query.filter(Staff.is_active == True).count(),
        'total_appointments_today': Appointment.query.filter(
            Appointment.appointment_date == today
        ).count(),
        'pending_bills': Bill.query.filter(
            Bill.status.in_(['pending', 'partially_paid'])
        ).count(),
        'low_stock_items': InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.minimum_stock,
            InventoryItem.is_active == True
        ).count()
    }
    
    # Recent activities
    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    
    # Revenue data for chart
    revenue_data = []
    for i in range(7):
        date_check = today - timedelta(days=i)
        daily_revenue = db.session.query(func.sum(Payment.amount)).filter(
            func.date(Payment.payment_date) == date_check
        ).scalar() or 0
        revenue_data.append({
            'date': date_check.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_patients=recent_patients,
                         recent_appointments=recent_appointments,
                         revenue_data=revenue_data)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage system users."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    role_filter = request.args.get('role', '', type=str)
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/manage_users.html', users=users, search=search, role_filter=role_filter)

@admin_bp.route('/users/<int:id>')
@login_required
@admin_required
def view_user(id):
    """View user details."""
    user = User.query.get_or_404(id)
    staff = None
    if user.role in ['doctor', 'nurse']:
        staff = Staff.query.filter_by(user_id=user.id).first()
    
    return render_template('admin/view_user.html', user=user, staff=staff)

@admin_bp.route('/users/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id):
    """Toggle user active status."""
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.view_user', id=id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    
    return redirect(url_for('admin.view_user', id=id))

@admin_bp.route('/staff')
@login_required
@admin_required
def manage_staff():
    """Manage hospital staff."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    department_filter = request.args.get('department', '', type=str)
    
    query = Staff.query
    
    if search:
        query = query.filter(
            db.or_(
                Staff.first_name.ilike(f'%{search}%'),
                Staff.last_name.ilike(f'%{search}%'),
                Staff.staff_id.ilike(f'%{search}%'),
                Staff.email.ilike(f'%{search}%')
            )
        )
    
    if department_filter:
        query = query.filter(Staff.department == department_filter)
    
    staff = query.order_by(Staff.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get unique departments for filter
    departments = db.session.query(Staff.department).distinct().all()
    departments = [dept[0] for dept in departments]
    
    return render_template('admin/manage_staff.html', 
                         staff=staff, 
                         search=search, 
                         department_filter=department_filter,
                         departments=departments)

@admin_bp.route('/staff/<int:id>')
@login_required
@admin_required
def view_staff(id):
    """View staff member details."""
    staff = Staff.query.get_or_404(id)
    
    # Get recent attendance
    recent_attendance = staff.attendance_records.order_by(
        AttendanceRecord.date.desc()
    ).limit(30).all()
    
    # Get upcoming appointments (if doctor)
    upcoming_appointments = []
    if staff.user.role == 'doctor':
        upcoming_appointments = staff.appointments.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.status.in_(['scheduled', 'confirmed'])
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(10).all()
    
    return render_template('admin/view_staff.html', 
                         staff=staff, 
                         recent_attendance=recent_attendance,
                         upcoming_appointments=upcoming_appointments)

@admin_bp.route('/staff/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_staff():
    """Add new staff member."""
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        department = request.form.get('department')
        specialization = request.form.get('specialization', '')
        qualification = request.form.get('qualification', '')
        
        # Validation
        if not all([username, email, password, role, first_name, last_name, gender, phone, department]):
            flash('All required fields must be filled.', 'error')
            return render_template('admin/add_staff.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('admin/add_staff.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('admin/add_staff.html')
        
        try:
            # Create user account
            user = User(username=username, email=email, password=password, role=role)
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create staff record
            staff = Staff(
                user_id=user.id,
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
            
            flash(f'Staff member {first_name} {last_name} added successfully!', 'success')
            return redirect(url_for('admin.view_staff', id=staff.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error adding staff member. Please try again.', 'error')
    
    return render_template('admin/add_staff.html')

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """System reports and analytics."""
    today = date.today()
    
    # Date range from request or default to last 30 days
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = today.strftime('%Y-%m-%d')
    
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Patient statistics
    patient_stats = {
        'total_registered': Patient.query.filter(
            Patient.created_at.between(start_date_obj, end_date_obj + timedelta(days=1))
        ).count(),
        'by_gender': db.session.query(
            Patient.gender, func.count(Patient.id)
        ).filter(
            Patient.created_at.between(start_date_obj, end_date_obj + timedelta(days=1))
        ).group_by(Patient.gender).all()
    }
    
    # Appointment statistics
    appointment_stats = {
        'total_appointments': Appointment.query.filter(
            Appointment.appointment_date.between(start_date_obj, end_date_obj)
        ).count(),
        'by_status': db.session.query(
            Appointment.status, func.count(Appointment.id)
        ).filter(
            Appointment.appointment_date.between(start_date_obj, end_date_obj)
        ).group_by(Appointment.status).all(),
        'by_type': db.session.query(
            Appointment.appointment_type, func.count(Appointment.id)
        ).filter(
            Appointment.appointment_date.between(start_date_obj, end_date_obj)
        ).group_by(Appointment.appointment_type).all()
    }
    
    # Revenue statistics
    revenue_stats = db.session.query(
        func.sum(Payment.amount).label('total_revenue'),
        func.count(Payment.id).label('total_payments')
    ).filter(
        Payment.payment_date.between(start_date_obj, end_date_obj)
    ).first()
    
    # Daily revenue for chart
    daily_revenue = []
    current_date = start_date_obj
    while current_date <= end_date_obj:
        day_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date == current_date
        ).scalar() or 0
        daily_revenue.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'revenue': float(day_revenue)
        })
        current_date += timedelta(days=1)
    
    return render_template('admin/reports.html',
                         patient_stats=patient_stats,
                         appointment_stats=appointment_stats,
                         revenue_stats=revenue_stats,
                         daily_revenue=daily_revenue,
                         start_date=start_date,
                         end_date=end_date)

@admin_bp.route('/system-settings')
@login_required
@admin_required
def system_settings():
    """System configuration and settings."""
    return render_template('admin/system_settings.html')

@admin_bp.route('/backup')
@login_required
@admin_required
def backup_system():
    """System backup functionality."""
    # In a real application, you would implement actual backup logic
    flash('System backup initiated. You will be notified when complete.', 'info')
    return redirect(url_for('admin.system_settings'))

@admin_bp.route('/logs')
@login_required
@admin_required
def view_logs():
    """View system logs."""
    # In a real application, you would implement log viewing
    return render_template('admin/logs.html')