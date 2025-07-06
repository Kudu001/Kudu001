from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.billing import Bill
from app.models.inventory import InventoryItem
from datetime import date, datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page - redirect to login or dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - redirects to role-specific dashboard."""
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
    
    # Fallback - show general dashboard
    return render_template('main/dashboard.html')

@main_bp.route('/search')
@login_required
def search():
    """Global search functionality."""
    query = request.args.get('q', '').strip()
    results = {
        'patients': [],
        'appointments': [],
        'staff': [],
        'inventory': []
    }
    
    if query and len(query) >= 2:
        # Search patients
        if current_user.can_manage_patients():
            patients = Patient.query.filter(
                db.or_(
                    Patient.first_name.ilike(f'%{query}%'),
                    Patient.last_name.ilike(f'%{query}%'),
                    Patient.patient_id.ilike(f'%{query}%'),
                    Patient.phone.ilike(f'%{query}%')
                )
            ).filter(Patient.is_active == True).limit(10).all()
            results['patients'] = [p.to_dict() for p in patients]
        
        # Search appointments
        if current_user.can_manage_appointments():
            appointments = Appointment.query.join(Patient).filter(
                db.or_(
                    Patient.first_name.ilike(f'%{query}%'),
                    Patient.last_name.ilike(f'%{query}%'),
                    Appointment.appointment_id.ilike(f'%{query}%')
                )
            ).limit(10).all()
            results['appointments'] = [a.to_dict() for a in appointments]
        
        # Search staff
        if current_user.can_manage_staff():
            staff = Staff.query.filter(
                db.or_(
                    Staff.first_name.ilike(f'%{query}%'),
                    Staff.last_name.ilike(f'%{query}%'),
                    Staff.staff_id.ilike(f'%{query}%'),
                    Staff.department.ilike(f'%{query}%')
                )
            ).filter(Staff.is_active == True).limit(10).all()
            results['staff'] = [s.to_dict() for s in staff]
        
        # Search inventory
        if current_user.can_manage_inventory():
            inventory = InventoryItem.query.filter(
                db.or_(
                    InventoryItem.name.ilike(f'%{query}%'),
                    InventoryItem.item_code.ilike(f'%{query}%'),
                    InventoryItem.category.ilike(f'%{query}%')
                )
            ).filter(InventoryItem.is_active == True).limit(10).all()
            results['inventory'] = [i.to_dict() for i in inventory]
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify(results)
    
    return render_template('main/search_results.html', query=query, results=results)

@main_bp.route('/notifications')
@login_required
def notifications():
    """Get user notifications."""
    notifications = []
    today = date.today()
    
    # Low stock alerts for nurses and admins
    if current_user.can_manage_inventory():
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.minimum_stock,
            InventoryItem.is_active == True
        ).all()
        
        for item in low_stock_items:
            notifications.append({
                'type': 'warning',
                'title': 'Low Stock Alert',
                'message': f'{item.name} is running low (Current: {item.current_stock}, Min: {item.minimum_stock})',
                'url': url_for('nurse.inventory') if current_user.role == 'nurse' else url_for('admin.inventory')
            })
    
    # Today's appointments for doctors
    if current_user.role == 'doctor' and current_user.staff:
        today_appointments = current_user.staff.get_today_appointments().all()
        for appointment in today_appointments:
            notifications.append({
                'type': 'info',
                'title': 'Today\'s Appointment',
                'message': f'Appointment with {appointment.patient.full_name} at {appointment.appointment_time.strftime("%H:%M")}',
                'url': url_for('doctor.appointment_detail', id=appointment.id)
            })
    
    # Overdue bills for accountants
    if current_user.can_manage_billing():
        overdue_bills = Bill.query.filter(
            Bill.due_date < today,
            Bill.status.in_(['pending', 'partial'])
        ).count()
        
        if overdue_bills > 0:
            notifications.append({
                'type': 'danger',
                'title': 'Overdue Bills',
                'message': f'{overdue_bills} bills are overdue',
                'url': url_for('accountant.bills')
            })
    
    return jsonify(notifications)

@main_bp.route('/stats')
@login_required
def get_stats():
    """Get dashboard statistics."""
    stats = {}
    
    if current_user.can_access_admin():
        # Admin stats
        stats.update({
            'total_patients': Patient.query.filter(Patient.is_active == True).count(),
            'total_staff': Staff.query.filter(Staff.is_active == True).count(),
            'today_appointments': Appointment.query.filter(
                db.func.date(Appointment.appointment_date) == date.today()
            ).count(),
            'pending_bills': Bill.query.filter(Bill.status == 'pending').count()
        })
    
    if current_user.role == 'doctor' and current_user.staff:
        # Doctor stats
        stats.update({
            'today_appointments': current_user.staff.get_today_appointments().count(),
            'total_patients': Appointment.query.filter(
                Appointment.doctor_id == current_user.staff.id
            ).distinct(Appointment.patient_id).count()
        })
    
    return jsonify(stats)