from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.billing import Bill
from app.models.inventory import InventoryItem
from datetime import date, datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/patients/search')
@login_required
def search_patients():
    """Search patients via AJAX."""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    patients = Patient.query.filter(
        db.or_(
            Patient.first_name.ilike(f'%{query}%'),
            Patient.last_name.ilike(f'%{query}%'),
            Patient.patient_id.ilike(f'%{query}%'),
            Patient.phone.ilike(f'%{query}%')
        ),
        Patient.is_active == True
    ).limit(10).all()
    
    return jsonify([p.to_dict() for p in patients])

@api_bp.route('/doctors/available')
@login_required
def available_doctors():
    """Get available doctors for appointment scheduling."""
    appointment_date = request.args.get('date')
    appointment_time = request.args.get('time')
    
    if not appointment_date or not appointment_time:
        return jsonify([])
    
    try:
        apt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        apt_time = datetime.strptime(appointment_time, '%H:%M').time()
    except ValueError:
        return jsonify([])
    
    # Get doctors from medical departments
    doctors = Staff.query.filter(
        Staff.department.in_(['Emergency', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics']),
        Staff.is_active == True
    ).all()
    
    available_doctors = []
    for doctor in doctors:
        if doctor.is_available_at(apt_date, apt_time):
            available_doctors.append(doctor.to_dict())
    
    return jsonify(available_doctors)

@api_bp.route('/appointments/slots')
@login_required
def available_slots():
    """Get available time slots for a doctor."""
    doctor_id = request.args.get('doctor_id')
    appointment_date = request.args.get('date')
    
    if not doctor_id or not appointment_date:
        return jsonify([])
    
    try:
        apt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify([])
    
    slots = Appointment.get_available_slots(doctor_id, apt_date)
    return jsonify(slots)

@api_bp.route('/stats/dashboard')
@login_required
def dashboard_stats():
    """Get dashboard statistics."""
    today = date.today()
    stats = {}
    
    if current_user.can_access_admin():
        stats = {
            'total_patients': Patient.query.filter(Patient.is_active == True).count(),
            'total_staff': Staff.query.filter(Staff.is_active == True).count(),
            'today_appointments': Appointment.query.filter(
                db.func.date(Appointment.appointment_date) == today
            ).count(),
            'pending_bills': Bill.query.filter(Bill.status == 'pending').count()
        }
    elif current_user.role == 'doctor' and current_user.staff:
        stats = {
            'today_appointments': current_user.staff.get_today_appointments().count(),
            'total_patients': db.session.query(Patient).join(Appointment).filter(
                Appointment.doctor_id == current_user.staff.id
            ).distinct().count()
        }
    elif current_user.role == 'nurse':
        stats = {
            'total_patients': Patient.query.filter(Patient.is_active == True).count(),
            'low_stock_items': InventoryItem.query.filter(
                InventoryItem.current_stock <= InventoryItem.minimum_stock,
                InventoryItem.is_active == True
            ).count()
        }
    elif current_user.role == 'receptionist':
        stats = {
            'total_patients': Patient.query.filter(Patient.is_active == True).count(),
            'today_appointments': Appointment.query.filter(
                db.func.date(Appointment.appointment_date) == today
            ).count()
        }
    elif current_user.role == 'accountant':
        from sqlalchemy import func
        stats = {
            'pending_bills': Bill.query.filter(Bill.status == 'pending').count(),
            'total_revenue': float(db.session.query(func.sum(Bill.paid_amount)).scalar() or 0)
        }
    
    return jsonify(stats)

@api_bp.route('/notifications')
@login_required
def get_notifications():
    """Get user notifications."""
    notifications = []
    
    # Low stock alerts
    if current_user.can_manage_inventory():
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.minimum_stock,
            InventoryItem.is_active == True
        ).limit(5).all()
        
        for item in low_stock_items:
            notifications.append({
                'type': 'warning',
                'title': 'Low Stock Alert',
                'message': f'{item.name} is running low'
            })
    
    # Today's appointments for doctors
    if current_user.role == 'doctor' and current_user.staff:
        today_appointments = current_user.staff.get_today_appointments().limit(3).all()
        for appointment in today_appointments:
            notifications.append({
                'type': 'info',
                'title': 'Today\'s Appointment',
                'message': f'Appointment with {appointment.patient.full_name} at {appointment.appointment_time.strftime("%H:%M")}'
            })
    
    return jsonify(notifications)

@api_bp.route('/inventory/<int:item_id>/stock', methods=['POST'])
@login_required
def update_stock(item_id):
    """Update inventory stock."""
    if not current_user.can_manage_inventory():
        return jsonify({'error': 'Access denied'}), 403
    
    item = InventoryItem.query.get_or_404(item_id)
    action = request.json.get('action')  # 'add' or 'remove'
    quantity = int(request.json.get('quantity', 0))
    reason = request.json.get('reason', '')
    
    try:
        if action == 'add':
            item.add_stock(quantity, reason, user_id=current_user.id)
            message = f'Added {quantity} {item.unit} to {item.name}'
        elif action == 'remove':
            item.remove_stock(quantity, reason, user_id=current_user.id)
            message = f'Removed {quantity} {item.unit} from {item.name}'
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        return jsonify({
            'success': True,
            'message': message,
            'current_stock': item.current_stock
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400