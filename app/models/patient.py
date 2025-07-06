from datetime import datetime, date
from app import db

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name='gender_types'), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(15))
    emergency_contact_relation = db.Column(db.String(50))
    
    # Medical Information
    blood_group = db.Column(db.Enum('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', name='blood_groups'))
    allergies = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    bills = db.relationship('Bill', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, first_name, last_name, date_of_birth, gender, phone, **kwargs):
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.phone = phone
        self.patient_id = self.generate_patient_id()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_patient_id(self):
        """Generate unique patient ID."""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f'P{timestamp}'
    
    @property
    def full_name(self):
        """Get patient's full name."""
        return f'{self.first_name} {self.last_name}'
    
    @property
    def age(self):
        """Calculate patient's age."""
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def get_recent_appointments(self, limit=5):
        """Get recent appointments."""
        return self.appointments.order_by(Appointment.appointment_date.desc()).limit(limit)
    
    def get_total_bills(self):
        """Get total amount of all bills."""
        total = db.session.query(db.func.sum(Bill.total_amount)).filter(Bill.patient_id == self.id).scalar()
        return total or 0
    
    def get_outstanding_bills(self):
        """Get total outstanding amount."""
        outstanding = db.session.query(db.func.sum(Bill.total_amount - Bill.paid_amount)).filter(
            Bill.patient_id == self.id,
            Bill.status != 'paid'
        ).scalar()
        return outstanding or 0
    
    def to_dict(self):
        """Convert patient to dictionary."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'blood_group': self.blood_group,
            'allergies': self.allergies,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Patient {self.patient_id}: {self.full_name}>'

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor = db.relationship('Staff', backref='medical_records')
    
    def __repr__(self):
        return f'<MedicalRecord {self.id}: Patient {self.patient_id}>'