from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.billing import Bill
from datetime import date, datetime, timedelta

receptionist_bp = Blueprint('receptionist', __name__)

def receptionist_required(f):
    """Decorator to require receptionist permissions."""
    def decorated_function(*args, **kwargs):
        if not current_user.can_manage_patients():
            flash('Access denied.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@receptionist_bp.route('/dashboard')
@login_required
@receptionist_required
def dashboard():
    """Receptionist dashboard."""
    today = date.today()
    
    # Today's statistics
    stats = {
        'total_patients': Patient.query.filter(Patient.is_active == True).count(),
        'new_patients_today': Patient.query.filter(
            db.func.date(Patient.created_at) == today
        ).count(),
        'appointments_today': Appointment.query.filter(
            Appointment.appointment_date == today
        ).count(),
        'pending_appointments': Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.status == 'scheduled'
        ).count()
    }
    
    # Today's appointments
    today_appointments = Appointment.query.filter(
        Appointment.appointment_date == today
    ).order_by(Appointment.appointment_time).all()
    
    # Recent patients
    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    
    # Upcoming appointments (next 7 days)
    week_end = today + timedelta(days=7)
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date.between(today, week_end),
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(10).all()
    
    return render_template('receptionist/dashboard.html',
                         stats=stats,
                         today_appointments=today_appointments,
                         recent_patients=recent_patients,
                         upcoming_appointments=upcoming_appointments)

@receptionist_bp.route('/patients')
@login_required
@receptionist_required
def manage_patients():
    """Manage patients."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Patient.query.filter(Patient.is_active == True)
    
    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.patient_id.ilike(f'%{search}%'),
                Patient.phone.ilike(f'%{search}%'),
                Patient.email.ilike(f'%{search}%')
            )
        )
    
    patients = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('receptionist/manage_patients.html', patients=patients, search=search)

@receptionist_bp.route('/patients/add', methods=['GET', 'POST'])
@login_required
@receptionist_required
def add_patient():
    """Add new patient."""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        email = request.form.get('email', '')
        address = request.form.get('address', '')
        
        # Emergency contact
        emergency_contact_name = request.form.get('emergency_contact_name', '')
        emergency_contact_phone = request.form.get('emergency_contact_phone', '')
        emergency_contact_relation = request.form.get('emergency_contact_relation', '')
        
        # Medical information
        blood_group = request.form.get('blood_group', '')
        allergies = request.form.get('allergies', '')
        medical_history = request.form.get('medical_history', '')
        current_medications = request.form.get('current_medications', '')
        
        # Validation
        if not all([first_name, last_name, date_of_birth, gender, phone]):
            flash('All required fields must be filled.', 'error')
            return render_template('receptionist/add_patient.html')
        
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format for date of birth.', 'error')
            return render_template('receptionist/add_patient.html')
        
        # Check if patient with same phone already exists
        existing_patient = Patient.query.filter_by(phone=phone).first()
        if existing_patient:
            flash('A patient with this phone number already exists.', 'warning')
            return redirect(url_for('receptionist.view_patient', id=existing_patient.id))
        
        try:
            # Create patient
            patient = Patient(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                gender=gender,
                phone=phone,
                email=email,
                address=address,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_phone=emergency_contact_phone,
                emergency_contact_relation=emergency_contact_relation,
                blood_group=blood_group if blood_group else None,
                allergies=allergies,
                medical_history=medical_history,
                current_medications=current_medications
            )
            db.session.add(patient)
            db.session.commit()
            
            flash(f'Patient {patient.full_name} registered successfully!', 'success')
            return redirect(url_for('receptionist.view_patient', id=patient.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error registering patient. Please try again.', 'error')
    
    return render_template('receptionist/add_patient.html')

@receptionist_bp.route('/patients/<int:id>')
@login_required
@receptionist_required
def view_patient(id):
    """View patient details."""
    patient = Patient.query.get_or_404(id)
    
    # Get recent appointments
    recent_appointments = patient.appointments.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).limit(10).all()
    
    # Get outstanding bills
    outstanding_bills = patient.bills.filter(
        Bill.status.in_(['pending', 'partially_paid'])
    ).all()
    
    return render_template('receptionist/view_patient.html',
                         patient=patient,
                         recent_appointments=recent_appointments,
                         outstanding_bills=outstanding_bills)

@receptionist_bp.route('/patients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@receptionist_required
def edit_patient(id):
    """Edit patient information."""
    patient = Patient.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update patient information
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.phone = request.form.get('phone')
        patient.email = request.form.get('email', '')
        patient.address = request.form.get('address', '')
        
        # Emergency contact
        patient.emergency_contact_name = request.form.get('emergency_contact_name', '')
        patient.emergency_contact_phone = request.form.get('emergency_contact_phone', '')
        patient.emergency_contact_relation = request.form.get('emergency_contact_relation', '')
        
        # Medical information
        blood_group = request.form.get('blood_group', '')
        patient.blood_group = blood_group if blood_group else None
        patient.allergies = request.form.get('allergies', '')
        patient.medical_history = request.form.get('medical_history', '')
        patient.current_medications = request.form.get('current_medications', '')
        
        try:
            db.session.commit()
            flash('Patient information updated successfully!', 'success')
            return redirect(url_for('receptionist.view_patient', id=patient.id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating patient information. Please try again.', 'error')
    
    return render_template('receptionist/edit_patient.html', patient=patient)

@receptionist_bp.route('/appointments')
@login_required
@receptionist_required
def manage_appointments():
    """Manage appointments."""
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    status_filter = request.args.get('status', '')
    doctor_filter = request.args.get('doctor', '', type=int)
    
    try:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except ValueError:
        filter_date = date.today()
    
    query = Appointment.query.filter(Appointment.appointment_date == filter_date)
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    if doctor_filter:
        query = query.filter(Appointment.doctor_id == doctor_filter)
    
    appointments = query.order_by(Appointment.appointment_time).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get doctors for filter
    doctors = Staff.query.filter(
        Staff.user.has(role='doctor'),
        Staff.is_active == True
    ).all()
    
    return render_template('receptionist/manage_appointments.html',
                         appointments=appointments,
                         date_filter=date_filter,
                         status_filter=status_filter,
                         doctor_filter=doctor_filter,
                         doctors=doctors)

@receptionist_bp.route('/appointments/book', methods=['GET', 'POST'])
@login_required
@receptionist_required
def book_appointment():
    """Book new appointment."""
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        appointment_type = request.form.get('appointment_type')
        reason_for_visit = request.form.get('reason_for_visit', '')
        
        # Validation
        if not all([patient_id, doctor_id, appointment_date, appointment_time, appointment_type]):
            flash('All required fields must be filled.', 'error')
            return render_template('receptionist/book_appointment.html')
        
        try:
            apt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            apt_time = datetime.strptime(appointment_time, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format.', 'error')
            return render_template('receptionist/book_appointment.html')
        
        # Check if patient and doctor exist
        patient = Patient.query.get(patient_id)
        doctor = Staff.query.get(doctor_id)
        
        if not patient or not doctor:
            flash('Invalid patient or doctor selected.', 'error')
            return render_template('receptionist/book_appointment.html')
        
        # Check if doctor is available
        if not doctor.is_available_at(apt_date, apt_time):
            flash('Doctor is not available at the selected time.', 'error')
            return render_template('receptionist/book_appointment.html')
        
        try:
            # Create appointment
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
            
            flash(f'Appointment booked successfully for {patient.full_name}!', 'success')
            return redirect(url_for('receptionist.view_appointment', id=appointment.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error booking appointment. Please try again.', 'error')
    
    # Get patients and doctors for form
    patients = Patient.query.filter(Patient.is_active == True).order_by(Patient.first_name).all()
    doctors = Staff.query.filter(
        Staff.user.has(role='doctor'),
        Staff.is_active == True,
        Staff.is_available == True
    ).order_by(Staff.first_name).all()
    
    return render_template('receptionist/book_appointment.html', patients=patients, doctors=doctors)

@receptionist_bp.route('/appointments/<int:id>')
@login_required
@receptionist_required
def view_appointment(id):
    """View appointment details."""
    appointment = Appointment.query.get_or_404(id)
    return render_template('receptionist/view_appointment.html', appointment=appointment)

@receptionist_bp.route('/appointments/<int:id>/cancel', methods=['POST'])
@login_required
@receptionist_required
def cancel_appointment(id):
    """Cancel appointment."""
    appointment = Appointment.query.get_or_404(id)
    
    if not appointment.can_be_cancelled():
        flash('This appointment cannot be cancelled.', 'error')
        return redirect(url_for('receptionist.view_appointment', id=id))
    
    reason = request.form.get('reason', 'Cancelled by receptionist')
    
    if appointment.cancel(reason):
        flash('Appointment cancelled successfully.', 'success')
    else:
        flash('Error cancelling appointment.', 'error')
    
    return redirect(url_for('receptionist.view_appointment', id=id))