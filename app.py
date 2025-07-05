from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from decimal import Decimal
import os

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///school_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models based on the SQL schema
class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    teacher_id = db.Column(db.Integer, primary_key=True)
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

# Routes
@app.route('/')
def index():
    # Get statistics for dashboard
    teachers_count = Teacher.query.count()
    students_count = Student.query.count()
    classes_count = Class.query.count()
    subjects_count = Subject.query.count()
    
    return render_template('index.html', 
                         teachers_count=teachers_count,
                         students_count=students_count,
                         classes_count=classes_count,
                         subjects_count=subjects_count)

@app.route('/teachers')
def teachers():
    teachers = Teacher.query.all()
    return render_template('teachers.html', teachers=teachers)

@app.route('/teachers/add', methods=['GET', 'POST'])
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
def students():
    students = Student.query.all()
    return render_template('students.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
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
            db.session.commit()
            flash('Class added successfully!', 'success')
            return redirect(url_for('classes'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding class.', 'error')
    
    teachers = Teacher.query.all()
    return render_template('add_class.html', teachers=teachers)

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

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)