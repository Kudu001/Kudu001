#!/usr/bin/env python3
"""
Hospital Management System Database Initialization Script

This script creates the database tables and populates them with sample data
for demonstration purposes.
"""

import os
import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.patient import Patient, MedicalRecord
from app.models.staff import Staff, StaffSchedule, AttendanceRecord
from app.models.appointment import Appointment
from app.models.billing import Bill, Payment, BillItem
from app.models.inventory import InventoryItem, UsageRecord, StockMovement

def init_database():
    """Initialize database with sample data."""
    print("🏥 Initializing Hospital Management System Database...")
    
    # Create all tables
    print("📊 Creating database tables...")
    db.create_all()
    
    # Check if data already exists
    if User.query.first():
        print("⚠️  Database already contains data. Skipping initialization.")
        return
    
    # Create sample users
    print("👥 Creating sample users...")
    users = [
        User('admin', 'admin@hospital.com', 'admin123', 'admin'),
        User('doctor', 'doctor@hospital.com', 'doctor123', 'doctor'),
        User('nurse', 'nurse@hospital.com', 'nurse123', 'nurse'),
        User('receptionist', 'receptionist@hospital.com', 'receptionist123', 'receptionist'),
        User('accountant', 'accountant@hospital.com', 'accountant123', 'accountant'),
    ]
    
    for user in users:
        db.session.add(user)
    
    db.session.commit()
    print(f"✅ Created {len(users)} users")
    
    # Create sample staff
    print("👨‍⚕️ Creating sample staff...")
    staff_members = [
        Staff('Dr. John', 'Smith', 'Male', '555-0101', 'john.smith@hospital.com', 'Cardiology',
              specialization='Interventional Cardiology', qualification='MD, FACC',
              experience_years=15, user_id=users[1].id),
        Staff('Dr. Sarah', 'Johnson', 'Female', '555-0102', 'sarah.johnson@hospital.com', 'Neurology',
              specialization='Pediatric Neurology', qualification='MD, PhD',
              experience_years=12, user_id=None),
        Staff('Emily', 'Davis', 'Female', '555-0103', 'emily.davis@hospital.com', 'Nursing',
              specialization='ICU Nursing', qualification='RN, BSN',
              experience_years=8, user_id=users[2].id),
        Staff('Michael', 'Brown', 'Male', '555-0104', 'michael.brown@hospital.com', 'Emergency',
              specialization='Emergency Medicine', qualification='MD, FACEP',
              experience_years=10, user_id=None),
    ]
    
    for staff in staff_members:
        db.session.add(staff)
    
    db.session.commit()
    print(f"✅ Created {len(staff_members)} staff members")
    
    # Create sample patients
    print("👥 Creating sample patients...")
    patients = [
        Patient('Alice', 'Cooper', date(1985, 3, 15), 'Female', '555-1001',
               email='alice.cooper@email.com', address='123 Main St, City, State',
               blood_group='A+', allergies='Penicillin'),
        Patient('Bob', 'Wilson', date(1978, 7, 22), 'Male', '555-1002',
               email='bob.wilson@email.com', address='456 Oak Ave, City, State',
               blood_group='O-', medical_history='Diabetes Type 2'),
        Patient('Carol', 'Martinez', date(1992, 11, 8), 'Female', '555-1003',
               email='carol.martinez@email.com', address='789 Pine St, City, State',
               blood_group='B+', allergies='Shellfish'),
        Patient('David', 'Lee', date(1965, 5, 30), 'Male', '555-1004',
               email='david.lee@email.com', address='321 Elm St, City, State',
               blood_group='AB+', medical_history='Hypertension'),
        Patient('Emma', 'Taylor', date(2000, 9, 12), 'Female', '555-1005',
               email='emma.taylor@email.com', address='654 Maple Ave, City, State',
               blood_group='A-', allergies='Latex'),
    ]
    
    for patient in patients:
        db.session.add(patient)
    
    db.session.commit()
    print(f"✅ Created {len(patients)} patients")
    
    # Create sample appointments
    print("📅 Creating sample appointments...")
    today = date.today()
    appointments = [
        Appointment(patients[0].id, staff_members[0].id, today + timedelta(days=1),
                   time(9, 0), 'Consultation', reason_for_visit='Chest pain',
                   consultation_fee=Decimal('150.00'), created_by=users[3].id),
        Appointment(patients[1].id, staff_members[1].id, today + timedelta(days=2),
                   time(10, 30), 'Follow-up', reason_for_visit='Diabetes checkup',
                   consultation_fee=Decimal('100.00'), created_by=users[3].id),
        Appointment(patients[2].id, staff_members[0].id, today + timedelta(days=3),
                   time(14, 0), 'Consultation', reason_for_visit='Heart palpitations',
                   consultation_fee=Decimal('150.00'), created_by=users[3].id),
        Appointment(patients[3].id, staff_members[3].id, today,
                   time(11, 0), 'Emergency', reason_for_visit='Severe headache',
                   consultation_fee=Decimal('200.00'), status='completed',
                   created_by=users[3].id),
        Appointment(patients[4].id, staff_members[1].id, today - timedelta(days=1),
                   time(15, 30), 'Checkup', reason_for_visit='Annual physical',
                   consultation_fee=Decimal('120.00'), status='completed',
                   created_by=users[3].id),
    ]
    
    for appointment in appointments:
        db.session.add(appointment)
    
    db.session.commit()
    print(f"✅ Created {len(appointments)} appointments")
    
    # Create sample inventory items
    print("💊 Creating sample inventory...")
    inventory_items = [
        InventoryItem('Paracetamol 500mg', 'Medicine', description='Pain reliever and fever reducer',
                     current_stock=450, minimum_stock=100, unit='tablets',
                     unit_price=Decimal('0.50'), manufacturer='PharmaCorp',
                     generic_name='Acetaminophen', requires_prescription=False,
                     created_by=users[0].id),
        InventoryItem('Surgical Gloves', 'Supplies', description='Latex-free surgical gloves',
                     current_stock=25, minimum_stock=50, unit='boxes',
                     unit_price=Decimal('15.00'), supplier_name='MedSupply Inc',
                     created_by=users[0].id),
        InventoryItem('Blood Pressure Monitor', 'Equipment', description='Digital BP monitor',
                     current_stock=8, minimum_stock=5, unit='pieces',
                     unit_price=Decimal('85.00'), supplier_name='MedTech Solutions',
                     created_by=users[0].id),
        InventoryItem('Insulin Pens', 'Medicine', description='Pre-filled insulin pens',
                     current_stock=12, minimum_stock=20, unit='pens',
                     unit_price=Decimal('25.00'), manufacturer='DiabetesCare',
                     generic_name='Insulin', requires_prescription=True,
                     created_by=users[0].id),
        InventoryItem('Face Masks', 'Supplies', description='Disposable surgical masks',
                     current_stock=5, minimum_stock=200, unit='boxes',
                     unit_price=Decimal('12.00'), supplier_name='SafetyFirst',
                     created_by=users[0].id),
    ]
    
    for item in inventory_items:
        db.session.add(item)
    
    db.session.commit()
    print(f"✅ Created {len(inventory_items)} inventory items")
    
    # Create sample bills
    print("💰 Creating sample bills...")
    bills = [
        Bill(patients[3].id, appointment_id=appointments[3].id, total_amount=Decimal('200.00'),
             paid_amount=Decimal('200.00'), status='paid', created_by=users[4].id),
        Bill(patients[4].id, appointment_id=appointments[4].id, total_amount=Decimal('120.00'),
             paid_amount=Decimal('60.00'), status='partial', created_by=users[4].id),
        Bill(patients[0].id, total_amount=Decimal('320.00'), paid_amount=Decimal('0.00'),
             status='pending', created_by=users[4].id),
    ]
    
    for bill in bills:
        db.session.add(bill)
    
    db.session.commit()
    
    # Create sample payments
    payments = [
        Payment(bills[0].id, Decimal('200.00'), 'cash', created_by=users[4].id),
        Payment(bills[1].id, Decimal('60.00'), 'card', reference_number='CC123456',
               created_by=users[4].id),
    ]
    
    for payment in payments:
        db.session.add(payment)
    
    db.session.commit()
    print(f"✅ Created {len(bills)} bills and {len(payments)} payments")
    
    # Create some medical records
    print("📋 Creating medical records...")
    medical_records = [
        MedicalRecord(
            patient_id=patients[3].id, 
            doctor_id=staff_members[3].id,
            symptoms='Severe headache, nausea, light sensitivity',
            diagnosis='Migraine with aura',
            prescription='Sumatriptan 50mg, rest in dark room',
            notes='Patient advised to avoid known triggers'
        ),
        MedicalRecord(
            patient_id=patients[4].id, 
            doctor_id=staff_members[1].id,
            symptoms='Routine checkup, no complaints',
            diagnosis='Healthy adult',
            prescription='Continue regular exercise and balanced diet',
            notes='Annual physical exam completed'
        ),
    ]
    
    for record in medical_records:
        db.session.add(record)
    
    db.session.commit()
    print(f"✅ Created {len(medical_records)} medical records")
    
    print("\n🎉 Database initialization completed successfully!")
    print("\n📋 Demo Login Credentials:")
    print("=" * 50)
    for user in users:
        print(f"Role: {user.role.title():<12} | Username: {user.username:<12} | Password: {user.username}123")
    print("=" * 50)

def main():
    """Main function to run database initialization."""
    app = create_app()
    
    with app.app_context():
        try:
            init_database()
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()
            return 1
    
    return 0

if __name__ == '__main__':
    exit(main())