from datetime import datetime, date, time, timedelta
from sqlalchemy import Numeric
from app import db

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    
    # Appointment Details
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, default=30)  # Duration in minutes
    appointment_type = db.Column(db.Enum('Consultation', 'Follow-up', 'Emergency', 'Checkup', 'Surgery', name='appointment_types'), nullable=False)
    status = db.Column(db.Enum('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show', name='appointment_status'), default='scheduled')
    
    # Additional Information
    reason_for_visit = db.Column(db.Text)
    notes = db.Column(db.Text)
    prescription = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    
    # Billing
    consultation_fee = db.Column(Numeric(10, 2), default=0.0)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', backref='created_appointments')
    
    def __init__(self, patient_id, doctor_id, appointment_date, appointment_time, appointment_type, **kwargs):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.appointment_type = appointment_type
        self.appointment_id = self.generate_appointment_id()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_appointment_id(self):
        """Generate unique appointment ID."""
        import random
        date_str = self.appointment_date.strftime('%Y%m%d') if self.appointment_date else datetime.now().strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        random_suffix = random.randint(100, 999)
        return f'APT{date_str}{timestamp}{random_suffix}'
    
    @property
    def appointment_datetime(self):
        """Get combined appointment datetime."""
        if self.appointment_date and self.appointment_time:
            return datetime.combine(self.appointment_date, self.appointment_time)
        return None
    
    @property
    def end_time(self):
        """Calculate appointment end time."""
        if self.appointment_time and self.duration:
            start_datetime = datetime.combine(date.today(), self.appointment_time)
            end_datetime = start_datetime + timedelta(minutes=self.duration)
            return end_datetime.time()
        return None
    
    def can_be_cancelled(self):
        """Check if appointment can be cancelled."""
        return self.status in ['scheduled', 'confirmed']
    
    def can_be_rescheduled(self):
        """Check if appointment can be rescheduled."""
        return self.status in ['scheduled', 'confirmed']
    
    def cancel(self, reason=None):
        """Cancel the appointment."""
        if self.can_be_cancelled():
            self.status = 'cancelled'
            if reason:
                self.notes = f"Cancelled: {reason}"
            db.session.commit()
            return True
        return False
    
    def complete(self, diagnosis=None, prescription=None, follow_up_required=False, follow_up_date=None):
        """Mark appointment as completed."""
        self.status = 'completed'
        if diagnosis:
            self.diagnosis = diagnosis
        if prescription:
            self.prescription = prescription
        self.follow_up_required = follow_up_required
        if follow_up_date:
            self.follow_up_date = follow_up_date
        db.session.commit()
    
    def confirm(self):
        """Confirm the appointment."""
        if self.status == 'scheduled':
            self.status = 'confirmed'
            db.session.commit()
    
    def start(self):
        """Start the appointment."""
        if self.status in ['scheduled', 'confirmed']:
            self.status = 'in_progress'
            db.session.commit()
    
    def is_today(self):
        """Check if appointment is today."""
        return self.appointment_date == date.today()
    
    def is_upcoming(self):
        """Check if appointment is upcoming."""
        return self.appointment_date >= date.today() and self.status in ['scheduled', 'confirmed']
    
    def is_past_due(self):
        """Check if appointment is past due."""
        if not self.appointment_datetime:
            return False
        return self.appointment_datetime < datetime.now() and self.status in ['scheduled', 'confirmed']
    
    def get_time_until_appointment(self):
        """Get time remaining until appointment."""
        if not self.appointment_datetime:
            return None
        
        now = datetime.now()
        if self.appointment_datetime > now:
            delta = self.appointment_datetime - now
            return delta
        return None
    
    def to_dict(self):
        """Convert appointment to dictionary."""
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'patient_name': self.patient.full_name if self.patient else '',
            'doctor_name': self.doctor.full_name if self.doctor else '',
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'appointment_type': self.appointment_type,
            'status': self.status,
            'reason_for_visit': self.reason_for_visit,
            'consultation_fee': float(self.consultation_fee) if self.consultation_fee else 0,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_available_slots(doctor_id, appointment_date, duration=30):
        """Get available time slots for a doctor on a specific date."""
        from datetime import timedelta
        
        # Define working hours (can be made configurable)
        start_time = time(9, 0)  # 9:00 AM
        end_time = time(17, 0)   # 5:00 PM
        
        # Get existing appointments for the doctor on that date
        existing_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status != 'cancelled'
        ).all()
        
        # Generate all possible time slots
        available_slots = []
        current_time = datetime.combine(appointment_date, start_time)
        end_datetime = datetime.combine(appointment_date, end_time)
        
        while current_time + timedelta(minutes=duration) <= end_datetime:
            slot_time = current_time.time()
            
            # Check if this slot conflicts with existing appointments
            is_available = True
            for appointment in existing_appointments:
                apt_start = datetime.combine(appointment_date, appointment.appointment_time)
                apt_end = apt_start + timedelta(minutes=appointment.duration)
                slot_start = current_time
                slot_end = current_time + timedelta(minutes=duration)
                
                # Check for overlap
                if not (slot_end <= apt_start or slot_start >= apt_end):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(slot_time.strftime('%H:%M'))
            
            current_time += timedelta(minutes=duration)
        
        return available_slots
    
    def __repr__(self):
        return f'<Appointment {self.appointment_id}: {self.patient.full_name if self.patient else "Unknown"} with {self.doctor.full_name if self.doctor else "Unknown"}>'