from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.patient import Patient, MedicalRecord
from app.models.appointment import Appointment
from app.models.staff import Staff
from datetime import date, datetime, timedelta

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    """Doctor dashboard."""
    # Get doctor's staff record
    staff = Staff.query.filter_by(user_id=current_user.id).first()
    if not staff:
        flash('Staff record not found. Please contact administrator.', 'error')
        return redirect(url_for('main.dashboard'))
    
    today = date.today()
    
    # Today's appointments
    today_appointments = staff.appointments.filter(
        Appointment.appointment_date == today
    ).order_by(Appointment.appointment_time).all()
    
    # Upcoming appointments
    upcoming_appointments = staff.appointments.filter(
        Appointment.appointment_date > today,
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(5).all()
    
    # Recent medical records
    recent_records = staff.medical_records.order_by(
        MedicalRecord.created_at.desc()
    ).limit(5).all()
    
    stats = {
        'appointments_today': len(today_appointments),
        'appointments_completed_today': len([a for a in today_appointments if a.status == 'completed']),
        'patients_treated_today': len(set(a.patient_id for a in today_appointments if a.status == 'completed')),
        'upcoming_appointments': len(upcoming_appointments)
    }
    
    return render_template('doctor/dashboard.html',
                         staff=staff,
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         recent_records=recent_records,
                         stats=stats)

@doctor_bp.route('/appointments')
@login_required
def appointments():
    """View appointments."""
    staff = Staff.query.filter_by(user_id=current_user.id).first()
    if not staff:
        return redirect(url_for('main.dashboard'))
    
    date_filter = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    try:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except ValueError:
        filter_date = date.today()
    
    appointments = staff.appointments.filter(
        Appointment.appointment_date == filter_date
    ).order_by(Appointment.appointment_time).all()
    
    return render_template('doctor/appointments.html',
                         appointments=appointments,
                         date_filter=date_filter)

@doctor_bp.route('/appointments/<int:id>')
@login_required
def view_appointment(id):
    """View appointment details."""
    appointment = Appointment.query.get_or_404(id)
    
    # Check if this appointment belongs to the current doctor
    staff = Staff.query.filter_by(user_id=current_user.id).first()
    if not staff or appointment.doctor_id != staff.id:
        flash('Access denied.', 'error')
        return redirect(url_for('doctor.appointments'))
    
    return render_template('doctor/view_appointment.html', appointment=appointment)

@doctor_bp.route('/patients/<int:id>')
@login_required
def view_patient(id):
    """View patient details."""
    patient = Patient.query.get_or_404(id)
    
    # Get medical records created by this doctor
    staff = Staff.query.filter_by(user_id=current_user.id).first()
    medical_records = patient.medical_records.filter(
        MedicalRecord.doctor_id == staff.id
    ).order_by(MedicalRecord.visit_date.desc()).all() if staff else []
    
    # Get patient's appointments with this doctor
    appointments = patient.appointments.filter(
        Appointment.doctor_id == staff.id
    ).order_by(Appointment.appointment_date.desc()).all() if staff else []
    
    return render_template('doctor/view_patient.html',
                         patient=patient,
                         medical_records=medical_records,
                         appointments=appointments)