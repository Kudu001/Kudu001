from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.staff import Staff
from datetime import date, datetime, time

receptionist_bp = Blueprint('receptionist', __name__)

def receptionist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'receptionist':
            flash('Access denied. Receptionist privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@receptionist_bp.route('/dashboard')
@login_required
@receptionist_required
def dashboard():
    """Receptionist dashboard."""
    today = date.today()
    
    # Today's appointments
    today_appointments = Appointment.query.filter(
        db.func.date(Appointment.appointment_date) == today
    ).order_by(Appointment.appointment_time).all()
    
    # Recent patients
    recent_patients = Patient.query.filter(Patient.is_active == True).order_by(
        Patient.created_at.desc()
    ).limit(5).all()
    
    # Statistics
    total_patients = Patient.query.filter(Patient.is_active == True).count()
    pending_appointments = Appointment.query.filter(
        Appointment.status == 'scheduled'
    ).count()
    
    return render_template('receptionist/dashboard.html',
                         today_appointments=today_appointments,
                         recent_patients=recent_patients,
                         total_patients=total_patients,
                         pending_appointments=pending_appointments)

@receptionist_bp.route('/patients')
@login_required
@receptionist_required
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
    
    return render_template('receptionist/patients.html', patients=patients, search=search)

@receptionist_bp.route('/patients/new', methods=['GET', 'POST'])
@login_required
@receptionist_required
def register_patient():
    """Register new patient."""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        
        # Convert date_of_birth
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date of birth.', 'error')
            return render_template('receptionist/register_patient.html')
        
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            gender=gender,
            phone=phone,
            email=email,
            address=address
        )
        
        db.session.add(patient)
        db.session.commit()
        
        flash(f'Patient {patient.full_name} registered successfully.', 'success')
        return redirect(url_for('receptionist.patients'))
    
    return render_template('receptionist/register_patient.html')

@receptionist_bp.route('/appointments')
@login_required
@receptionist_required
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
            query = query.filter(db.func.date(Appointment.appointment_date) == filter_date)
        except ValueError:
            pass
    
    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('receptionist/appointments.html',
                         appointments=appointments,
                         selected_status=status,
                         selected_date=date_filter)

@receptionist_bp.route('/appointments/new', methods=['GET', 'POST'])
@login_required
@receptionist_required
def schedule_appointment():
    """Schedule new appointment."""
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        appointment_type = request.form.get('appointment_type')
        reason_for_visit = request.form.get('reason_for_visit')
        
        # Convert date and time
        try:
            apt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            apt_time = datetime.strptime(appointment_time, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time.', 'error')
            return render_template('receptionist/schedule_appointment.html')
        
        # Check if doctor is available
        doctor = Staff.query.get(doctor_id)
        if not doctor.is_available_at(apt_date, apt_time):
            flash('Doctor is not available at this time.', 'error')
            return render_template('receptionist/schedule_appointment.html')
        
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=apt_date,
            appointment_time=apt_time,
            appointment_type=appointment_type,
            reason_for_visit=reason_for_visit,
            created_by=current_user.id
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment scheduled successfully.', 'success')
        return redirect(url_for('receptionist.appointments'))
    
    # Get patients and doctors for the form
    patients = Patient.query.filter(Patient.is_active == True).order_by(Patient.first_name).all()
    doctors = Staff.query.filter(
        Staff.department.in_(['Emergency', 'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics']),
        Staff.is_active == True
    ).order_by(Staff.first_name).all()
    
    return render_template('receptionist/schedule_appointment.html',
                         patients=patients,
                         doctors=doctors)

@receptionist_bp.route('/appointments/<int:appointment_id>/confirm')
@login_required
@receptionist_required
def confirm_appointment(appointment_id):
    """Confirm appointment."""
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.confirm()
    flash('Appointment confirmed.', 'success')
    return redirect(url_for('receptionist.appointments'))

@receptionist_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@receptionist_required
def cancel_appointment(appointment_id):
    """Cancel appointment."""
    appointment = Appointment.query.get_or_404(appointment_id)
    reason = request.form.get('reason', 'Cancelled by receptionist')
    
    if appointment.cancel(reason):
        flash('Appointment cancelled.', 'success')
    else:
        flash('Cannot cancel this appointment.', 'error')
    
    return redirect(url_for('receptionist.appointments'))

@receptionist_bp.route('/schedule')
@login_required
@receptionist_required
def schedule():
    """View daily schedule."""
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
        db.func.date(Appointment.appointment_date) == selected_date
    ).order_by(Appointment.appointment_time).all()
    
    return render_template('receptionist/schedule.html',
                         appointments=appointments,
                         selected_date=selected_date)