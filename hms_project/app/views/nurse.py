from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.inventory import InventoryItem, UsageRecord
from app.models.staff import Staff
from datetime import date, datetime

nurse_bp = Blueprint('nurse', __name__)

def nurse_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'nurse':
            flash('Access denied. Nurse privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@nurse_bp.route('/dashboard')
@login_required
@nurse_required
def dashboard():
    """Nurse dashboard."""
    today = date.today()
    
    # Today's appointments requiring nursing assistance
    today_appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) == today,
        Appointment.status.in_(['scheduled', 'confirmed', 'in_progress'])
    ).order_by(Appointment.appointment_time).limit(10).all()
    
    # Low stock items
    low_stock_items = InventoryItem.query.filter(
        InventoryItem.current_stock <= InventoryItem.minimum_stock,
        InventoryItem.is_active == True
    ).limit(5).all()
    
    # Recent patients
    recent_patients = Patient.query.filter(Patient.is_active == True).order_by(
        Patient.created_at.desc()
    ).limit(5).all()
    
    # Statistics
    total_patients = Patient.query.filter(Patient.is_active == True).count()
    critical_stock_items = InventoryItem.query.filter(
        InventoryItem.current_stock <= 5,
        InventoryItem.is_active == True
    ).count()
    
    return render_template('nurse/dashboard.html',
                         today_appointments=today_appointments,
                         low_stock_items=low_stock_items,
                         recent_patients=recent_patients,
                         total_patients=total_patients,
                         critical_stock_items=critical_stock_items)

@nurse_bp.route('/patients')
@login_required
@nurse_required
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
                Patient.patient_id.ilike(f'%{search}%')
            )
        )
    
    patients = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('nurse/patients.html', patients=patients, search=search)

@nurse_bp.route('/inventory')
@login_required
@nurse_required
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
    
    return render_template('nurse/inventory.html',
                         items=items,
                         categories=categories,
                         selected_category=category,
                         low_stock_filter=low_stock)

@nurse_bp.route('/inventory/<int:item_id>/use', methods=['POST'])
@login_required
@nurse_required
def use_inventory_item(item_id):
    """Use inventory item."""
    item = InventoryItem.query.get_or_404(item_id)
    quantity = int(request.form.get('quantity', 1))
    patient_id = request.form.get('patient_id')
    notes = request.form.get('notes', '')
    
    try:
        usage = item.use_item(
            quantity=quantity,
            used_by_id=current_user.id,
            patient_id=patient_id if patient_id else None,
            notes=notes
        )
        flash(f'Used {quantity} {item.unit} of {item.name}', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('nurse.inventory'))

@nurse_bp.route('/appointments')
@login_required
@nurse_required
def appointments():
    """View appointments for nursing assistance."""
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date', '')
    
    query = Appointment.query
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Appointment.appointment_date) == filter_date)
        except ValueError:
            pass
    else:
        # Default to today and upcoming
        query = query.filter(Appointment.appointment_date >= date.today())
    
    appointments = query.order_by(
        Appointment.appointment_date,
        Appointment.appointment_time
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('nurse/appointments.html',
                         appointments=appointments,
                         selected_date=date_filter)

@nurse_bp.route('/schedule')
@login_required
@nurse_required
def schedule():
    """View nursing schedule."""
    selected_date = request.args.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Get appointments for selected date
    appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) == selected_date,
        Appointment.status.in_(['scheduled', 'confirmed', 'in_progress'])
    ).order_by(Appointment.appointment_time).all()
    
    return render_template('nurse/schedule.html',
                         appointments=appointments,
                         selected_date=selected_date)