from datetime import datetime, date, time
from app import db

class Staff(db.Model):
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name='staff_gender'), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text)
    
    # Professional Information
    department = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    qualification = db.Column(db.String(200))
    license_number = db.Column(db.String(50))
    experience_years = db.Column(db.Integer, default=0)
    
    # Employment Information
    hire_date = db.Column(db.Date, default=date.today)
    salary = db.Column(db.Decimal(10, 2))
    shift = db.Column(db.Enum('Morning', 'Evening', 'Night', 'Rotating', name='shift_types'), default='Morning')
    is_available = db.Column(db.Boolean, default=True)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')
    schedules = db.relationship('StaffSchedule', backref='staff', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='staff', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, user_id, first_name, last_name, gender, phone, email, department, **kwargs):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.phone = phone
        self.email = email
        self.department = department
        self.staff_id = self.generate_staff_id()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_staff_id(self):
        """Generate unique staff ID based on department."""
        department_codes = {
            'Emergency': 'ER',
            'Cardiology': 'CD',
            'Neurology': 'NR',
            'Orthopedics': 'OR',
            'Pediatrics': 'PD',
            'Radiology': 'RD',
            'Laboratory': 'LB',
            'Nursing': 'NS',
            'Administration': 'AD',
            'Pharmacy': 'PH'
        }
        
        dept_code = department_codes.get(self.department, 'GN')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f'{dept_code}{timestamp}'
    
    @property
    def full_name(self):
        """Get staff's full name."""
        return f'{self.first_name} {self.last_name}'
    
    @property
    def age(self):
        """Calculate staff's age."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def get_today_appointments(self):
        """Get today's appointments for this staff member."""
        today = date.today()
        return self.appointments.filter(
            db.func.date(Appointment.appointment_date) == today,
            Appointment.status != 'cancelled'
        ).order_by(Appointment.appointment_time)
    
    def get_weekly_schedule(self):
        """Get this week's schedule."""
        from datetime import timedelta
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        return self.schedules.filter(
            StaffSchedule.work_date.between(week_start, week_end)
        ).order_by(StaffSchedule.work_date)
    
    def is_available_at(self, appointment_date, appointment_time):
        """Check if staff is available at given date and time."""
        # Check if staff has conflicting appointments
        existing_appointment = Appointment.query.filter(
            Appointment.doctor_id == self.id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status != 'cancelled'
        ).first()
        
        return existing_appointment is None and self.is_available
    
    def to_dict(self):
        """Convert staff to dictionary."""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'department': self.department,
            'specialization': self.specialization,
            'qualification': self.qualification,
            'phone': self.phone,
            'email': self.email,
            'is_available': self.is_available,
            'shift': self.shift
        }
    
    def __repr__(self):
        return f'<Staff {self.staff_id}: {self.full_name}>'

class StaffSchedule(db.Model):
    __tablename__ = 'staff_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    shift_type = db.Column(db.Enum('Morning', 'Evening', 'Night', name='schedule_shifts'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Schedule {self.staff_id}: {self.work_date}>'

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.Time)
    check_out_time = db.Column(db.Time)
    status = db.Column(db.Enum('Present', 'Absent', 'Late', 'Half Day', name='attendance_status'), default='Present')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def hours_worked(self):
        """Calculate hours worked."""
        if self.check_in_time and self.check_out_time:
            check_in = datetime.combine(self.date, self.check_in_time)
            check_out = datetime.combine(self.date, self.check_out_time)
            delta = check_out - check_in
            return delta.total_seconds() / 3600
        return 0
    
    def __repr__(self):
        return f'<Attendance {self.staff_id}: {self.date}>'