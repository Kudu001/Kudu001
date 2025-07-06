from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.patient import Patient, MedicalRecord
from app.models.appointment import Appointment
from app.models.staff import Staff
from datetime import date, datetime, timedelta

doctor_bp = Blueprint('doctor', __name__)

def doctor_required(f):
    """Decorator to require doctor role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
            flash('Access denied. Doctor privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@doctor_bp.route('/dashboard')
@login_required
@doctor_required
def dashboard():
    """Doctor dashboard."""
    today = date.today()
    
    # Get doctor's staff record
    doctor_staff = current_user.staff
    if not doctor_staff:
        flash('No staff record found. Please contact admin.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Today's appointments
    today_appointments = doctor_staff.get_today_appointments().all()
    
    # Upcoming appointments (next 7 days)
    next_week = today + timedelta(days=7)
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_staff.id,
        Appointment.appointment_date > today,
        Appointment.appointment_date <= next_week,
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(10).all()
    
    # Recent patients
    recent_patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor_staff.id,
        Appointment.status == 'completed'
    ).distinct().order_by(Appointment.appointment_date.desc()).limit(5).all()
    
    # Statistics
    total_patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor_staff.id
    ).distinct().count()
    
    completed_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_staff.id,
        Appointment.status == 'completed'
    ).count()
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor_staff,
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         recent_patients=recent_patients,
                         total_patients=total_patients,
                         completed_appointments=completed_appointments)

@doctor_bp.route('/appointments')
@login_required
@doctor_required
def appointments():
    """View doctor's appointments."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    
    doctor_staff = current_user.staff
    query = Appointment.query.filter(Appointment.doctor_id == doctor_staff.id)
    
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
    
    return render_template('doctor/appointments.html',
                         appointments=appointments,
                         selected_status=status,
                         selected_date=date_filter)

@doctor_bp.route('/appointments/<int:appointment_id>')
@login_required
@doctor_required
def appointment_detail(appointment_id):
    """View appointment details."""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Ensure this appointment belongs to the current doctor
    if appointment.doctor_id != current_user.staff.id:
        flash('Access denied.', 'error')
        return redirect(url_for('doctor.appointments'))
    
    return render_template('doctor/appointment_detail.html', appointment=appointment)

@doctor_bp.route('/appointments/<int:appointment_id>/start')
@login_required
@doctor_required
def start_appointment(appointment_id):
    """Start an appointment."""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.doctor_id != current_user.staff.id:
        flash('Access denied.', 'error')
        return redirect(url_for('doctor.appointments'))
    
    appointment.start()
    flash('Appointment started.', 'success')
    return redirect(url_for('doctor.consultation', appointment_id=appointment_id))

@doctor_bp.route('/appointments/<int:appointment_id>/consultation', methods=['GET', 'POST'])
@login_required
@doctor_required
def consultation(appointment_id):
    """Conduct consultation."""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.doctor_id != current_user.staff.id:
        flash('Access denied.', 'error')
        return redirect(url_for('doctor.appointments'))
    
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')
        follow_up_required = request.form.get('follow_up_required') == 'on'
        follow_up_date = request.form.get('follow_up_date')
        
        # Create medical record
        medical_record = MedicalRecord(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            symptoms=symptoms,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes
        )
        
        if follow_up_date:
            try:
                medical_record.follow_up_date = datetime.strptime(follow_up_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        db.session.add(medical_record)
        
        # Complete appointment
        appointment.complete(
            diagnosis=diagnosis,
            prescription=prescription,
            follow_up_required=follow_up_required,
            follow_up_date=medical_record.follow_up_date
        )
        
        flash('Consultation completed successfully.', 'success')
        return redirect(url_for('doctor.appointments'))
    
    return render_template('doctor/consultation.html', appointment=appointment)

@doctor_bp.route('/patients')
@login_required
@doctor_required
def patients():
    """View doctor's patients."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    doctor_staff = current_user.staff
    query = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor_staff.id
    ).distinct()
    
    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.patient_id.ilike(f'%{search}%')
            )
        )
    
    patients = query.order_by(Patient.first_name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('doctor/patients.html', patients=patients, search=search)

@doctor_bp.route('/patients/<int:patient_id>')
@login_required
@doctor_required
def patient_detail(patient_id):
    """View patient details."""
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if doctor has treated this patient
    has_treated = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.doctor_id == current_user.staff.id
    ).first()
    
    if not has_treated:
        flash('Access denied.', 'error')
        return redirect(url_for('doctor.patients'))
    
    # Get patient's medical records with this doctor
    medical_records = MedicalRecord.query.filter(
        MedicalRecord.patient_id == patient_id,
        MedicalRecord.doctor_id == current_user.staff.id
    ).order_by(MedicalRecord.visit_date.desc()).all()
    
    # Get appointment history
    appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.doctor_id == current_user.staff.id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctor/patient_detail.html',
                         patient=patient,
                         medical_records=medical_records,
                         appointments=appointments)

@doctor_bp.route('/schedule')
@login_required
@doctor_required
def schedule():
    """View doctor's schedule."""
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
        Appointment.doctor_id == current_user.staff.id,
        db.func.date(Appointment.appointment_date) == selected_date
    ).order_by(Appointment.appointment_time).all()
    
    return render_template('doctor/schedule.html',
                         appointments=appointments,
                         selected_date=selected_date)

@doctor_bp.route('/reports')
@login_required
@doctor_required
def reports():
    """Doctor reports."""
    doctor_staff = current_user.staff
    
    # Statistics
    total_patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor_staff.id
    ).distinct().count()
    
    total_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_staff.id
    ).count()
    
    completed_consultations = Appointment.query.filter(
        Appointment.doctor_id == doctor_staff.id,
        Appointment.status == 'completed'
    ).count()
    
    # Monthly consultation data
    monthly_data = []
    for i in range(6):
        month_start = date.today().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end - timedelta(days=month_end.day)
        
        consultations = Appointment.query.filter(
            Appointment.doctor_id == doctor_staff.id,
            Appointment.appointment_date >= month_start,
            Appointment.appointment_date <= month_end,
            Appointment.status == 'completed'
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'consultations': consultations
        })
    
    monthly_data.reverse()
    
    return render_template('doctor/reports.html',
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         completed_consultations=completed_consultations,
                         monthly_data=monthly_data)