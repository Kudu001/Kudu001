from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.billing import Bill
from app.models.inventory import InventoryItem
from datetime import date, datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page - redirect to login if not authenticated."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with role-based redirects."""
    # Redirect to role-specific dashboard
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    elif current_user.role == 'nurse':
        return redirect(url_for('nurse.dashboard'))
    elif current_user.role == 'receptionist':
        return redirect(url_for('receptionist.dashboard'))
    elif current_user.role == 'accountant':
        return redirect(url_for('accountant.dashboard'))
    
    # Fallback to general dashboard
    return render_template('main/dashboard.html')

@main_bp.route('/search')
@login_required
def search():
    """Global search functionality."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'results': []})
    
    results = []
    
    # Search patients (if user can manage patients)
    if current_user.can_manage_patients():
        patients = Patient.query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{query}%'),
                Patient.last_name.ilike(f'%{query}%'),
                Patient.patient_id.ilike(f'%{query}%'),
                Patient.phone.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        for patient in patients:
            results.append({
                'type': 'patient',
                'id': patient.id,
                'title': patient.full_name,
                'subtitle': f'ID: {patient.patient_id} | Phone: {patient.phone}',
                'url': url_for('receptionist.view_patient', id=patient.id)
            })
    
    # Search staff (if user can manage staff)
    if current_user.can_manage_staff():
        staff = Staff.query.filter(
            db.or_(
                Staff.first_name.ilike(f'%{query}%'),
                Staff.last_name.ilike(f'%{query}%'),
                Staff.staff_id.ilike(f'%{query}%'),
                Staff.department.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        for staff_member in staff:
            results.append({
                'type': 'staff',
                'id': staff_member.id,
                'title': staff_member.full_name,
                'subtitle': f'ID: {staff_member.staff_id} | {staff_member.department}',
                'url': url_for('admin.view_staff', id=staff_member.id)
            })
    
    return jsonify({'results': results})

@main_bp.route('/notifications')
@login_required
def notifications():
    """Get user notifications."""
    notifications = []
    today = date.today()
    
    # Low stock alerts (for nurses and admin)
    if current_user.can_manage_inventory():
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.minimum_stock,
            InventoryItem.is_active == True
        ).limit(5).all()
        
        for item in low_stock_items:
            notifications.append({
                'type': 'warning',
                'title': 'Low Stock Alert',
                'message': f'{item.name} is running low (Current: {item.current_stock})',
                'timestamp': datetime.now().isoformat(),
                'url': url_for('nurse.inventory')
            })
    
    # Today's appointments (for doctors and receptionists)
    if current_user.role in ['doctor', 'receptionist']:
        today_appointments = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status.in_(['scheduled', 'confirmed'])
        )
        
        if current_user.role == 'doctor':
            # Only show appointments for this doctor
            staff = Staff.query.filter_by(user_id=current_user.id).first()
            if staff:
                today_appointments = today_appointments.filter(
                    Appointment.doctor_id == staff.id
                )
        
        today_appointments = today_appointments.limit(5).all()
        
        for appointment in today_appointments:
            notifications.append({
                'type': 'info',
                'title': 'Today\'s Appointment',
                'message': f'{appointment.patient.full_name} at {appointment.appointment_time.strftime("%H:%M")}',
                'timestamp': datetime.now().isoformat(),
                'url': url_for('doctor.view_appointment', id=appointment.id) if current_user.role == 'doctor' else url_for('receptionist.view_appointment', id=appointment.id)
            })
    
    # Overdue bills (for accountants and admin)
    if current_user.can_manage_billing():
        overdue_bills = Bill.query.filter(
            Bill.due_date < today,
            Bill.status.in_(['pending', 'partially_paid'])
        ).limit(5).all()
        
        for bill in overdue_bills:
            notifications.append({
                'type': 'error',
                'title': 'Overdue Bill',
                'message': f'Bill {bill.bill_number} for {bill.patient.full_name} is overdue',
                'timestamp': datetime.now().isoformat(),
                'url': url_for('accountant.view_bill', id=bill.id)
            })
    
    return jsonify({'notifications': notifications})

@main_bp.route('/quick-stats')
@login_required
def quick_stats():
    """Get quick statistics for dashboard widgets."""
    stats = {}
    today = date.today()
    
    # Patient stats
    if current_user.can_manage_patients():
        stats['total_patients'] = Patient.query.filter(Patient.is_active == True).count()
        stats['new_patients_today'] = Patient.query.filter(
            db.func.date(Patient.created_at) == today
        ).count()
    
    # Appointment stats
    if current_user.can_manage_appointments():
        stats['total_appointments_today'] = Appointment.query.filter(
            Appointment.appointment_date == today
        ).count()
        stats['pending_appointments'] = Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.status == 'scheduled'
        ).count()
    
    # Billing stats
    if current_user.can_manage_billing():
        stats['pending_bills'] = Bill.query.filter(
            Bill.status.in_(['pending', 'partially_paid'])
        ).count()
        
        # Total revenue today
        today_payments = db.session.query(db.func.sum(Bill.paid_amount)).filter(
            db.func.date(Bill.created_at) == today
        ).scalar() or 0
        stats['revenue_today'] = float(today_payments)
    
    # Inventory stats
    if current_user.can_manage_inventory():
        stats['low_stock_items'] = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.minimum_stock,
            InventoryItem.is_active == True
        ).count()
        stats['out_of_stock_items'] = InventoryItem.query.filter(
            InventoryItem.current_stock <= 0,
            InventoryItem.is_active == True
        ).count()
    
    # Staff stats (admin only)
    if current_user.can_manage_staff():
        stats['total_staff'] = Staff.query.filter(Staff.is_active == True).count()
        stats['available_doctors'] = Staff.query.filter(
            Staff.is_active == True,
            Staff.is_available == True,
            Staff.user.has(role='doctor')
        ).count()
    
    return jsonify(stats)

@main_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 errors."""
    return render_template('errors/403.html'), 403

@main_bp.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('errors/500.html'), 500