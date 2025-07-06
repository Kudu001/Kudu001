from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import check_password_hash, generate_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum('admin', 'doctor', 'nurse', 'receptionist', 'accountant', name='user_roles'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship with staff table
    staff = db.relationship('Staff', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        """Check if user has specific role."""
        return self.role == role
    
    def can_access_admin(self):
        """Check if user can access admin features."""
        return self.role == 'admin'
    
    def can_manage_patients(self):
        """Check if user can manage patients."""
        return self.role in ['admin', 'doctor', 'nurse', 'receptionist']
    
    def can_manage_appointments(self):
        """Check if user can manage appointments."""
        return self.role in ['admin', 'doctor', 'receptionist']
    
    def can_manage_staff(self):
        """Check if user can manage staff."""
        return self.role == 'admin'
    
    def can_manage_billing(self):
        """Check if user can manage billing."""
        return self.role in ['admin', 'accountant', 'receptionist']
    
    def can_manage_inventory(self):
        """Check if user can manage inventory."""
        return self.role in ['admin', 'nurse']
    
    def can_view_reports(self):
        """Check if user can view reports."""
        return self.role in ['admin', 'doctor', 'accountant']
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'