from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.billing import Bill
from app.models.inventory import InventoryItem
from datetime import date, datetime, timedelta

api_bp = Blueprint('api', __name__)

@api_bp.route('/patients/search')
@login_required
def search_patients():
    """Search patients by name, ID, or phone."""
    if not current_user.can_manage_patients():
        return jsonify({'error': 'Access denied'}), 403
    
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'patients': []})
    
    patients = Patient.query.filter(
        db.or_(
            Patient.first_name.ilike(f'%{query}%'),
            Patient.last_name.ilike(f'%{query}%'),
            Patient.patient_id.ilike(f'%{query}%'),
            Patient.phone.ilike(f'%{query}%')
        ),
        Patient.is_active == True
    ).limit(10).all()
    
    return jsonify({
        'patients': [patient.to_dict() for patient in patients]
    })

@api_bp.route('/doctors/available')
@login_required
def available_doctors():
    """Get available doctors for appointment booking."""
    if not current_user.can_manage_appointments():
        return jsonify({'error': 'Access denied'}), 403
    
    date_str = request.args.get('date')
    time_str = request.args.get('time')
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(time_str, '%H:%M').time()
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date or time format'}), 400
    
    # Get all doctors
    doctors = Staff.query.filter(
        Staff.user.has(role='doctor'),
        Staff.is_active == True,
        Staff.is_available == True
    ).all()
    
    available_doctors = []
    for doctor in doctors:
        if doctor.is_available_at(appointment_date, appointment_time):
            available_doctors.append(doctor.to_dict())
    
    return jsonify({'doctors': available_doctors})

@api_bp.route('/appointments/slots')
@login_required
def available_slots():
    """Get available time slots for a doctor on a specific date."""
    if not current_user.can_manage_appointments():
        return jsonify({'error': 'Access denied'}), 403
    
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date')
    
    if not doctor_id or not date_str:
        return jsonify({'error': 'Doctor ID and date are required'}), 400
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Check if doctor exists
    doctor = Staff.query.get(doctor_id)
    if not doctor or doctor.user.role != 'doctor':
        return jsonify({'error': 'Doctor not found'}), 404
    
    slots = Appointment.get_available_slots(doctor_id, appointment_date)
    return jsonify({'slots': slots})

@api_bp.route('/inventory/low-stock')
@login_required
def low_stock_items():
    """Get low stock inventory items."""
    if not current_user.can_manage_inventory():
        return jsonify({'error': 'Access denied'}), 403
    
    items = InventoryItem.query.filter(
        InventoryItem.current_stock <= InventoryItem.minimum_stock,
        InventoryItem.is_active == True
    ).all()
    
    return jsonify({
        'items': [item.to_dict() for item in items]
    })

@api_bp.route('/bills/patient/<int:patient_id>')
@login_required
def patient_bills():
    """Get bills for a specific patient."""
    if not current_user.can_manage_billing():
        return jsonify({'error': 'Access denied'}), 403
    
    patient = Patient.query.get_or_404(patient_id)
    bills = patient.bills.order_by(Bill.created_at.desc()).limit(10).all()
    
    return jsonify({
        'bills': [bill.to_dict() for bill in bills]
    })

@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics based on user role."""
    today = date.today()
    stats = {}
    
    if current_user.can_manage_patients():
        stats['patients'] = {
            'total': Patient.query.filter(Patient.is_active == True).count(),
            'new_today': Patient.query.filter(
                db.func.date(Patient.created_at) == today
            ).count()
        }
    
    if current_user.can_manage_appointments():
        stats['appointments'] = {
            'today': Appointment.query.filter(
                Appointment.appointment_date == today
            ).count(),
            'pending': Appointment.query.filter(
                Appointment.appointment_date >= today,
                Appointment.status == 'scheduled'
            ).count()
        }
    
    if current_user.can_manage_billing():
        stats['billing'] = {
            'pending_bills': Bill.query.filter(
                Bill.status.in_(['pending', 'partially_paid'])
            ).count(),
            'overdue_bills': Bill.query.filter(
                Bill.due_date < today,
                Bill.status.in_(['pending', 'partially_paid'])
            ).count()
        }
    
    if current_user.can_manage_inventory():
        stats['inventory'] = {
            'low_stock': InventoryItem.query.filter(
                InventoryItem.current_stock <= InventoryItem.minimum_stock,
                InventoryItem.is_active == True
            ).count(),
            'out_of_stock': InventoryItem.query.filter(
                InventoryItem.current_stock <= 0,
                InventoryItem.is_active == True
            ).count()
        }
    
    return jsonify(stats)

@api_bp.route('/appointments/<int:appointment_id>/status', methods=['POST'])
@login_required
def update_appointment_status():
    """Update appointment status."""
    if not current_user.can_manage_appointments():
        return jsonify({'error': 'Access denied'}), 403
    
    appointment_id = request.view_args['appointment_id']
    appointment = Appointment.query.get_or_404(appointment_id)
    
    new_status = request.json.get('status')
    if new_status not in ['confirmed', 'in_progress', 'completed', 'cancelled', 'no_show']:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        appointment.status = new_status
        if new_status == 'completed':
            diagnosis = request.json.get('diagnosis')
            prescription = request.json.get('prescription')
            if diagnosis:
                appointment.diagnosis = diagnosis
            if prescription:
                appointment.prescription = prescription
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Appointment status updated to {new_status}'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update appointment status'}), 500

@api_bp.route('/inventory/<int:item_id>/stock', methods=['POST'])
@login_required
def update_inventory_stock():
    """Update inventory stock levels."""
    if not current_user.can_manage_inventory():
        return jsonify({'error': 'Access denied'}), 403
    
    item_id = request.view_args['item_id']
    item = InventoryItem.query.get_or_404(item_id)
    
    action = request.json.get('action')  # 'add' or 'use'
    quantity = request.json.get('quantity', 0)
    notes = request.json.get('notes', '')
    
    if not action or quantity <= 0:
        return jsonify({'error': 'Invalid action or quantity'}), 400
    
    try:
        if action == 'add':
            success = item.add_stock(quantity, notes, current_user.id)
        elif action == 'use':
            success = item.use_stock(quantity, 'consumption', notes, current_user.id)
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Stock {action}ed successfully',
                'new_stock': item.current_stock
            })
        else:
            return jsonify({'error': 'Insufficient stock or invalid operation'}), 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update stock'}), 500

@api_bp.route('/patients/<int:patient_id>/appointments')
@login_required
def patient_appointments():
    """Get appointments for a specific patient."""
    if not current_user.can_manage_patients():
        return jsonify({'error': 'Access denied'}), 403
    
    patient = Patient.query.get_or_404(patient_id)
    appointments = patient.appointments.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).limit(10).all()
    
    return jsonify({
        'appointments': [appointment.to_dict() for appointment in appointments]
    })

@api_bp.route('/reports/revenue-chart')
@login_required
def revenue_chart_data():
    """Get revenue data for charts."""
    if not current_user.can_view_reports():
        return jsonify({'error': 'Access denied'}), 403
    
    days = request.args.get('days', 30, type=int)
    today = date.today()
    
    revenue_data = []
    for i in range(days):
        check_date = today - timedelta(days=i)
        daily_revenue = db.session.query(db.func.sum(Bill.paid_amount)).filter(
            db.func.date(Bill.created_at) == check_date
        ).scalar() or 0
        
        revenue_data.append({
            'date': check_date.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })
    
    revenue_data.reverse()  # Show oldest to newest
    return jsonify({'data': revenue_data})