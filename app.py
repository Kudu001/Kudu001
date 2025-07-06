from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, DecimalField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Optional
from datetime import datetime, date
from decimal import Decimal
from functools import wraps
import os
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///school_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt(app)

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role-based access control decorator
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Models based on the SQL schema
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.Enum('admin', 'teacher', 'student', 'parent', name='user_roles'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False)
    student_profile = db.relationship('Student', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    teacher_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    specialization = db.Column(db.String(100))
    
    # Relationships
    classes = db.relationship('Class', backref='homeroom_teacher', lazy=True)
    class_subjects = db.relationship('ClassSubject', backref='teacher', lazy=True)
    
    def __repr__(self):
        return f'<Teacher {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Class(db.Model):
    __tablename__ = 'classes'
    
    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'))
    
    # Relationships
    students = db.relationship('Student', backref='current_class', lazy=True)
    class_subjects = db.relationship('ClassSubject', backref='class_ref', lazy=True)
    
    def __repr__(self):
        return f'<Class {self.class_name} ({self.academic_year})>'

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name='gender_enum'))
    enrollment_date = db.Column(db.Date, nullable=False, default=date.today)
    current_class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'))
    address = db.Column(db.Text)
    contact_number = db.Column(db.String(20))
    parent_guardian_name = db.Column(db.String(100))
    parent_guardian_contact = db.Column(db.String(20))
    
    # Relationships
    grades = db.relationship('Grade', backref='student', lazy=True)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    
    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationships
    class_subjects = db.relationship('ClassSubject', backref='subject', lazy=True)
    
    def __repr__(self):
        return f'<Subject {self.subject_name}>'

class ClassSubject(db.Model):
    __tablename__ = 'class_subjects'
    
    class_subject_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=False)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('class_id', 'subject_id', name='unique_class_subject'),)
    
    # Relationships
    grades = db.relationship('Grade', backref='class_subject', lazy=True)
    
    def __repr__(self):
        return f'<ClassSubject {self.class_ref.class_name} - {self.subject.subject_name}>'

class Grade(db.Model):
    __tablename__ = 'grades'
    
    grade_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    class_subject_id = db.Column(db.Integer, db.ForeignKey('class_subjects.class_subject_id'), nullable=False)
    term = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Numeric(5, 2))
    date_recorded = db.Column(db.Date, nullable=False, default=date.today)
    
    def __repr__(self):
        return f'<Grade {self.student.full_name} - {self.score}>'

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Present', 'Absent', 'Late', 'Excused', name='attendance_status'), nullable=False)
    notes = db.Column(db.Text)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('student_id', 'date', name='unique_student_date'),)
    
    def __repr__(self):
        return f'<Attendance {self.student.full_name} - {self.date} - {self.status}>'

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer)
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.user.username} - {self.action} - {self.table_name}>'

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('teacher', 'Teacher'), ('student', 'Student'), ('parent', 'Parent')], validators=[DataRequired()])

# Audit logging function
def log_audit(action, table_name, record_id=None, old_values=None, new_values=None):
    if current_user.is_authenticated:
        audit_log = AuditLog(
            user_id=current_user.id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=str(old_values) if old_values else None,
            new_values=str(new_values) if new_values else None,
            ip_address=request.remote_addr
        )
        db.session.add(audit_log)
        # Don't commit here, let the calling function handle the commit

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Username already exists.', 'error')
        elif existing_email:
            flash('Email already registered.', 'error')
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Routes
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics for dashboard
    teachers_count = Teacher.query.count()
    students_count = Student.query.count()
    classes_count = Class.query.count()
    subjects_count = Subject.query.count()
    
    # Get recent activity data
    from sqlalchemy import func
    today = date.today()
    
    new_users_today = User.query.filter(func.date(User.created_at) == today).count()
    new_grades_today = Grade.query.filter(Grade.date_recorded == today).count()
    attendance_today = Attendance.query.filter(Attendance.date == today).count()
    active_users = User.query.filter(User.is_active == True).count()
    
    return render_template('index.html', 
                         teachers_count=teachers_count,
                         students_count=students_count,
                         classes_count=classes_count,
                         subjects_count=subjects_count,
                         new_users_today=new_users_today,
                         new_grades_today=new_grades_today,
                         attendance_today=attendance_today,
                         active_users=active_users)

@app.route('/teachers')
@login_required
@role_required(['admin', 'teacher'])
def teachers():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)

@app.route('/teachers/add', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def add_teacher():
    if request.method == 'POST':
        teacher = Teacher(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            contact_number=request.form['contact_number'],
            email=request.form['email'],
            specialization=request.form['specialization']
        )
        try:
            db.session.add(teacher)
            db.session.commit()
            flash('Teacher added successfully!', 'success')
            return redirect(url_for('teachers'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding teacher. Email might already exist.', 'error')
    
    return render_template('add_teacher.html')

@app.route('/students')
@login_required
@role_required(['admin', 'teacher'])
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def add_student():
    if request.method == 'POST':
        student = Student(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            date_of_birth=datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date() if request.form['date_of_birth'] else None,
            gender=request.form['gender'],
            current_class_id=request.form['current_class_id'] if request.form['current_class_id'] else None,
            address=request.form['address'],
            contact_number=request.form['contact_number'],
            parent_guardian_name=request.form['parent_guardian_name'],
            parent_guardian_contact=request.form['parent_guardian_contact']
        )
        try:
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding student.', 'error')
    
    classes = Class.query.all()
    return render_template('add_student.html', classes=classes)

@app.route('/classes')
def classes():
    classes = Class.query.all()
    return render_template('classes.html', classes=classes)

@app.route('/classes/add', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        class_obj = Class(
            class_name=request.form['class_name'],
            academic_year=request.form['academic_year'],
            teacher_id=request.form['teacher_id'] if request.form['teacher_id'] else None
        )
        try:
            db.session.add(class_obj)
            db.session.flush()  # Flush to get the class_id
            
            # Handle subject assignments
            subject_ids = request.form.getlist('subject_ids[]')
            subject_teacher_ids = request.form.getlist('subject_teacher_ids[]')
            
            for i, subject_id in enumerate(subject_ids):
                if subject_id and i < len(subject_teacher_ids) and subject_teacher_ids[i]:
                    # Check if this subject is already assigned to this class
                    existing = ClassSubject.query.filter_by(
                        class_id=class_obj.class_id,
                        subject_id=subject_id
                    ).first()
                    
                    if not existing:
                        class_subject = ClassSubject(
                            class_id=class_obj.class_id,
                            subject_id=subject_id,
                            teacher_id=subject_teacher_ids[i]
                        )
                        db.session.add(class_subject)
            
            db.session.commit()
            flash('Class and subjects added successfully!', 'success')
            return redirect(url_for('classes'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding class and subjects.', 'error')
    
    teachers = Teacher.query.all()
    subjects = Subject.query.all()
    return render_template('add_class.html', teachers=teachers, subjects=subjects)

@app.route('/classes/<int:class_id>/subjects', methods=['GET', 'POST'])
def manage_class_subjects(class_id):
    class_obj = Class.query.get_or_404(class_id)
    
    if request.method == 'POST':
        # Remove existing class subjects
        ClassSubject.query.filter_by(class_id=class_id).delete()
        
        # Add new subject assignments
        subject_ids = request.form.getlist('subject_ids[]')
        subject_teacher_ids = request.form.getlist('subject_teacher_ids[]')
        
        try:
            for i, subject_id in enumerate(subject_ids):
                if subject_id and i < len(subject_teacher_ids) and subject_teacher_ids[i]:
                    class_subject = ClassSubject(
                        class_id=class_id,
                        subject_id=subject_id,
                        teacher_id=subject_teacher_ids[i]
                    )
                    db.session.add(class_subject)
            
            db.session.commit()
            flash('Class subjects updated successfully!', 'success')
            return redirect(url_for('classes'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating class subjects.', 'error')
    
    teachers = Teacher.query.all()
    subjects = Subject.query.all()
    current_assignments = ClassSubject.query.filter_by(class_id=class_id).all()
    
    return render_template('manage_class_subjects.html', 
                         class_obj=class_obj, 
                         teachers=teachers, 
                         subjects=subjects,
                         current_assignments=current_assignments)

@app.route('/subjects')
def subjects():
    subjects = Subject.query.all()
    return render_template('subjects.html', subjects=subjects)

@app.route('/subjects/add', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        subject = Subject(
            subject_name=request.form['subject_name']
        )
        try:
            db.session.add(subject)
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('subjects'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding subject. Subject might already exist.', 'error')
    
    return render_template('add_subject.html')

@app.route('/grades')
def grades():
    grades = Grade.query.all()
    return render_template('grades.html', grades=grades)

@app.route('/grades/add', methods=['GET', 'POST'])
def add_grade():
    if request.method == 'POST':
        grade = Grade(
            student_id=request.form['student_id'],
            class_subject_id=request.form['class_subject_id'],
            term=request.form['term'],
            score=Decimal(request.form['score']) if request.form['score'] else None
        )
        try:
            db.session.add(grade)
            db.session.commit()
            flash('Grade added successfully!', 'success')
            return redirect(url_for('grades'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding grade.', 'error')
    
    students = Student.query.all()
    class_subjects = ClassSubject.query.all()
    return render_template('add_grade.html', students=students, class_subjects=class_subjects)

@app.route('/attendance')
def attendance():
    attendance_records = Attendance.query.order_by(Attendance.date.desc()).all()
    return render_template('attendance.html', attendance_records=attendance_records)

@app.route('/attendance/add', methods=['GET', 'POST'])
def add_attendance():
    if request.method == 'POST':
        attendance = Attendance(
            student_id=request.form['student_id'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            status=request.form['status'],
            notes=request.form['notes']
        )
        try:
            db.session.add(attendance)
            db.session.commit()
            flash('Attendance recorded successfully!', 'success')
            return redirect(url_for('attendance'))
        except Exception as e:
            db.session.rollback()
            flash('Error recording attendance. Record might already exist for this date.', 'error')
    
    students = Student.query.all()
    return render_template('add_attendance.html', students=students, today=date.today())

# API endpoints for AJAX calls
@app.route('/api/students/<int:class_id>')
def api_students_by_class(class_id):
    students = Student.query.filter_by(current_class_id=class_id).all()
    return jsonify([{
        'student_id': s.student_id,
        'full_name': s.full_name
    } for s in students])

@app.route('/api/class_subjects/<int:class_id>')
def api_class_subjects(class_id):
    class_subjects = ClassSubject.query.filter_by(class_id=class_id).all()
    return jsonify([{
        'class_subject_id': cs.class_subject_id,
        'subject_name': cs.subject.subject_name,
        'teacher_name': cs.teacher.full_name
    } for cs in class_subjects])

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Add sample data if tables are empty
        if User.query.count() == 0:
            # Create default admin user
            admin_user = User(
                username='admin',
                email='admin@school.edu',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            # Create sample teacher users
            teacher_users = [
                User(username='john_smith', email='john.smith@school.edu', role='teacher'),
                User(username='sarah_johnson', email='sarah.johnson@school.edu', role='teacher'),
                User(username='michael_brown', email='michael.brown@school.edu', role='teacher'),
                User(username='emily_davis', email='emily.davis@school.edu', role='teacher')
            ]
            
            for user in teacher_users:
                user.set_password('teacher123')
                db.session.add(user)
            
            db.session.commit()
        
        if Teacher.query.count() == 0:
            sample_teachers = [
                Teacher(first_name='John', last_name='Smith', email='john.smith@school.edu', specialization='Mathematics'),
                Teacher(first_name='Sarah', last_name='Johnson', email='sarah.johnson@school.edu', specialization='English Literature'),
                Teacher(first_name='Michael', last_name='Brown', email='michael.brown@school.edu', specialization='Science'),
                Teacher(first_name='Emily', last_name='Davis', email='emily.davis@school.edu', specialization='History')
            ]
            
            sample_subjects = [
                Subject(subject_name='Mathematics'),
                Subject(subject_name='English'),
                Subject(subject_name='Science'),
                Subject(subject_name='History'),
                Subject(subject_name='Physical Education'),
                Subject(subject_name='Art'),
                Subject(subject_name='Music')
            ]
            
            for teacher in sample_teachers:
                db.session.add(teacher)
            for subject in sample_subjects:
                db.session.add(subject)
            
            db.session.commit()
            
            # Add sample classes
            sample_classes = [
                Class(class_name='Grade 9A', academic_year='2023-2024', teacher_id=1),
                Class(class_name='Grade 9B', academic_year='2023-2024', teacher_id=2),
                Class(class_name='Grade 10A', academic_year='2023-2024', teacher_id=3),
                Class(class_name='Grade 10B', academic_year='2023-2024', teacher_id=4)
            ]
            
            for class_obj in sample_classes:
                db.session.add(class_obj)
            
            db.session.commit()
            
            # Add sample class-subject assignments
            sample_assignments = [
                ClassSubject(class_id=1, subject_id=1, teacher_id=1),  # Grade 9A - Math - John
                ClassSubject(class_id=1, subject_id=2, teacher_id=2),  # Grade 9A - English - Sarah
                ClassSubject(class_id=1, subject_id=3, teacher_id=3),  # Grade 9A - Science - Michael
                ClassSubject(class_id=2, subject_id=1, teacher_id=1),  # Grade 9B - Math - John
                ClassSubject(class_id=2, subject_id=2, teacher_id=2),  # Grade 9B - English - Sarah
                ClassSubject(class_id=3, subject_id=1, teacher_id=1),  # Grade 10A - Math - John
                ClassSubject(class_id=3, subject_id=4, teacher_id=4),  # Grade 10A - History - Emily
            ]
            
            for assignment in sample_assignments:
                db.session.add(assignment)
            
                         db.session.commit()

# Report Generation Routes
@app.route('/reports')
@login_required
@role_required(['admin', 'teacher'])
def reports():
    return render_template('reports.html')

@app.route('/reports/students/pdf')
@login_required
@role_required(['admin', 'teacher'])
def export_students_pdf():
    # Create PDF report
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Get data
    students = Student.query.all()
    
    # Create content
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    content = []
    content.append(Paragraph("Student Report", title_style))
    content.append(Spacer(1, 20))
    
    # Create table data
    data = [['ID', 'Name', 'Gender', 'Class', 'Enrollment Date']]
    for student in students:
        data.append([
            str(student.student_id),
            student.full_name,
            student.gender or 'N/A',
            student.current_class.class_name if student.current_class else 'Not assigned',
            student.enrollment_date.strftime('%Y-%m-%d') if student.enrollment_date else 'N/A'
        ])
    
    # Create table
    table = Table(data, colWidths=[0.8*inch, 2*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(table)
    doc.build(content)
    
    buffer.seek(0)
    
    # Log audit
    log_audit('EXPORT_PDF', 'students')
    db.session.commit()
    
    return buffer.getvalue(), 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename=students_report_{date.today()}.pdf'
    }

@app.route('/reports/students/excel')
@login_required
@role_required(['admin', 'teacher'])
def export_students_excel():
    # Get data
    students = Student.query.all()
    
    # Create DataFrame
    data = []
    for student in students:
        data.append({
            'ID': student.student_id,
            'First Name': student.first_name,
            'Last Name': student.last_name,
            'Gender': student.gender,
            'Date of Birth': student.date_of_birth,
            'Class': student.current_class.class_name if student.current_class else 'Not assigned',
            'Address': student.address,
            'Contact': student.contact_number,
            'Guardian': student.parent_guardian_name,
            'Guardian Contact': student.parent_guardian_contact,
            'Enrollment Date': student.enrollment_date
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Students', index=False)
    
    buffer.seek(0)
    
    # Log audit
    log_audit('EXPORT_EXCEL', 'students')
    db.session.commit()
    
    return buffer.getvalue(), 200, {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': f'attachment; filename=students_report_{date.today()}.xlsx'
    }

@app.route('/reports/grades/pdf')
@login_required
@role_required(['admin', 'teacher'])
def export_grades_pdf():
    # Create PDF report for grades
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Get data
    grades = Grade.query.join(Student).join(ClassSubject).join(Subject).all()
    
    # Create content
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    
    content = []
    content.append(Paragraph("Grades Report", title_style))
    content.append(Spacer(1, 20))
    
    # Create table data
    data = [['Student', 'Subject', 'Term', 'Score', 'Date']]
    for grade in grades:
        data.append([
            grade.student.full_name,
            grade.class_subject.subject.subject_name,
            grade.term,
            str(grade.score) if grade.score else 'N/A',
            grade.date_recorded.strftime('%Y-%m-%d')
        ])
    
    # Create table
    table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    content.append(table)
    doc.build(content)
    
    buffer.seek(0)
    
    # Log audit
    log_audit('EXPORT_PDF', 'grades')
    db.session.commit()
    
    return buffer.getvalue(), 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename=grades_report_{date.today()}.pdf'
    }

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)