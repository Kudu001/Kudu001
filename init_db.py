#!/usr/bin/env python3
"""
Hospital Management System - Database Initialization Script

This script initializes the database with tables and sample data.
Run this script to set up the HMS database for development/testing.
"""

import os
from datetime import date, datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.patient import Patient
from app.models.staff import Staff
from app.models.appointment import Appointment
from app.models.billing import Bill, BillItem, Payment
from app.models.inventory import InventoryItem, UsageRecord

def init_database():
    """Initialize database with tables and sample data."""
    app = create_app('development')
    
    with app.app_context():
        print("🏥 Initializing Hospital Management System Database...")
        
        # Drop all tables and recreate
        print("📋 Dropping existing tables...")
        db.drop_all()
        
        print("🏗️  Creating tables...")
        db.create_all()
        
        # Create default users
        print("👤 Creating default users...")
        create_default_users()
        
        # Create staff records
        print("👨‍⚕️ Creating staff records...")
        create_staff_records()
        
        # Create sample patients
        print("🤕 Creating sample patients...")
        create_sample_patients()
        
        # Create sample appointments
        print("📅 Creating sample appointments...")
        create_sample_appointments()
        
        # Create sample inventory
        print("📦 Creating sample inventory...")
        create_sample_inventory()
        
        # Create sample bills
        print("💰 Creating sample bills...")
        create_sample_bills()
        
        print("✅ Database initialization completed successfully!")
        print("\n🔑 Default Login Credentials:")
        print("   Admin:        admin / admin123")
        print("   Doctor:       doctor / doctor123")
        print("   Nurse:        nurse / nurse123")
        print("   Receptionist: receptionist / recep123")
        print("   Accountant:   accountant / account123")

def create_default_users():
    """Create default users for each role."""
    users = [
        User('admin', 'admin@hospital.com', 'admin123', 'admin'),
        User('doctor', 'doctor@hospital.com', 'doctor123', 'doctor'),
        User('nurse', 'nurse@hospital.com', 'nurse123', 'nurse'),
        User('receptionist', 'receptionist@hospital.com', 'recep123', 'receptionist'),
        User('accountant', 'accountant@hospital.com', 'account123', 'accountant'),
    ]
    
    for user in users:
        db.session.add(user)
    
    db.session.commit()

def create_staff_records():
    """Create staff records for medical personnel."""
    # Get users
    doctor_user = User.query.filter_by(username='doctor').first()
    nurse_user = User.query.filter_by(username='nurse').first()
    
    staff_records = [
        Staff(
            user_id=doctor_user.id,
            first_name='Dr. John',
            last_name='Smith',
            gender='Male',
            phone='555-0101',
            email='doctor@hospital.com',
            department='Cardiology',
            specialization='Cardiovascular Surgery',
            qualification='MD, FRCS',
            experience_years=15,
            salary=150000.00
        ),
        Staff(
            user_id=nurse_user.id,
            first_name='Sarah',
            last_name='Johnson',
            gender='Female',
            phone='555-0102',
            email='nurse@hospital.com',
            department='Nursing',
            specialization='Critical Care',
            qualification='RN, BSN',
            experience_years=8,
            salary=75000.00
        ),
        # Additional doctors
        Staff(
            user_id=None,  # Will create without user account
            first_name='Dr. Emily',
            last_name='Davis',
            gender='Female',
            phone='555-0103',
            email='emily.davis@hospital.com',
            department='Pediatrics',
            specialization='Pediatric Care',
            qualification='MD, FAAP',
            experience_years=10,
            salary=140000.00
        ),
        Staff(
            user_id=None,
            first_name='Dr. Michael',
            last_name='Brown',
            gender='Male',
            phone='555-0104',
            email='michael.brown@hospital.com',
            department='Emergency',
            specialization='Emergency Medicine',
            qualification='MD, FACEP',
            experience_years=12,
            salary=160000.00
        ),
    ]
    
    # Create user accounts for additional doctors
    additional_doctors = [
        User('emily.davis', 'emily.davis@hospital.com', 'doctor123', 'doctor'),
        User('michael.brown', 'michael.brown@hospital.com', 'doctor123', 'doctor'),
    ]
    
    for user in additional_doctors:
        db.session.add(user)
    db.session.flush()
    
    # Update staff records with user IDs
    staff_records[2].user_id = additional_doctors[0].id
    staff_records[3].user_id = additional_doctors[1].id
    
    for staff in staff_records:
        db.session.add(staff)
    
    db.session.commit()

def create_sample_patients():
    """Create sample patients."""
    patients = [
        Patient(
            first_name='Alice',
            last_name='Wilson',
            date_of_birth=date(1985, 3, 15),
            gender='Female',
            phone='555-1001',
            email='alice.wilson@email.com',
            address='123 Main St, City, State 12345',
            blood_group='A+',
            allergies='Penicillin',
            medical_history='Hypertension, Diabetes Type 2'
        ),
        Patient(
            first_name='Robert',
            last_name='Johnson',
            date_of_birth=date(1978, 7, 22),
            gender='Male',
            phone='555-1002',
            email='robert.johnson@email.com',
            address='456 Oak Ave, City, State 12345',
            blood_group='O-',
            medical_history='Asthma'
        ),
        Patient(
            first_name='Maria',
            last_name='Garcia',
            date_of_birth=date(1990, 11, 8),
            gender='Female',
            phone='555-1003',
            email='maria.garcia@email.com',
            address='789 Pine St, City, State 12345',
            blood_group='B+',
            allergies='Shellfish'
        ),
        Patient(
            first_name='David',
            last_name='Lee',
            date_of_birth=date(1965, 5, 30),
            gender='Male',
            phone='555-1004',
            address='321 Elm St, City, State 12345',
            blood_group='AB+',
            medical_history='High cholesterol, Previous heart surgery'
        ),
        Patient(
            first_name='Emma',
            last_name='Thompson',
            date_of_birth=date(2010, 9, 12),
            gender='Female',
            phone='555-1005',
            email='emma.parent@email.com',
            address='654 Maple Dr, City, State 12345',
            blood_group='A-',
            emergency_contact_name='Jennifer Thompson',
            emergency_contact_phone='555-1006',
            emergency_contact_relation='Mother'
        ),
    ]
    
    for patient in patients:
        db.session.add(patient)
    
    db.session.commit()

def create_sample_appointments():
    """Create sample appointments."""
    patients = Patient.query.all()
    doctors = Staff.query.filter(Staff.user_id.isnot(None)).all()
    
    today = date.today()
    appointments = []
    
    # Create appointments for the next few days
    for i, patient in enumerate(patients[:4]):
        appointment_date = today + timedelta(days=i)
        appointment_time = datetime.strptime(f'{9 + i}:00', '%H:%M').time()
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctors[i % len(doctors)].id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            appointment_type='Consultation',
            reason_for_visit=f'Regular checkup for {patient.first_name}',
            consultation_fee=150.00
        )
        appointments.append(appointment)
    
    # Create some completed appointments
    for i, patient in enumerate(patients):
        past_date = today - timedelta(days=i + 1)
        past_time = datetime.strptime(f'{10 + i}:30', '%H:%M').time()
        
        completed_appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctors[i % len(doctors)].id,
            appointment_date=past_date,
            appointment_time=past_time,
            appointment_type='Follow-up',
            reason_for_visit='Follow-up visit',
            status='completed',
            diagnosis='Patient in good health',
            prescription='Continue current medications',
            consultation_fee=100.00
        )
        appointments.append(completed_appointment)
    
    for appointment in appointments:
        db.session.add(appointment)
    
    db.session.commit()

def create_sample_inventory():
    """Create sample inventory items."""
    inventory_items = [
        InventoryItem(
            name='Paracetamol 500mg',
            category='Medication',
            description='Pain relief and fever reducer',
            current_stock=500,
            minimum_stock=50,
            maximum_stock=1000,
            unit_of_measure='tablets',
            unit_cost=0.50,
            selling_price=1.00,
            supplier_name='MedSupply Co.'
        ),
        InventoryItem(
            name='Disposable Syringes',
            category='Supplies',
            description='10ml disposable syringes',
            current_stock=8,  # Low stock
            minimum_stock=50,
            maximum_stock=500,
            unit_of_measure='pieces',
            unit_cost=0.25,
            selling_price=0.50,
            supplier_name='MedEquip Ltd.'
        ),
        InventoryItem(
            name='Digital Thermometer',
            category='Equipment',
            description='Digital oral thermometer',
            current_stock=25,
            minimum_stock=10,
            maximum_stock=50,
            unit_of_measure='pieces',
            unit_cost=15.00,
            selling_price=25.00,
            supplier_name='HealthTech Inc.'
        ),
        InventoryItem(
            name='Surgical Masks',
            category='Supplies',
            description='Disposable surgical masks',
            current_stock=0,  # Out of stock
            minimum_stock=100,
            maximum_stock=1000,
            unit_of_measure='pieces',
            unit_cost=0.10,
            selling_price=0.25,
            supplier_name='SafetyFirst Co.'
        ),
        InventoryItem(
            name='Blood Pressure Monitor',
            category='Equipment',
            description='Digital blood pressure monitor',
            current_stock=15,
            minimum_stock=5,
            maximum_stock=25,
            unit_of_measure='pieces',
            unit_cost=80.00,
            selling_price=150.00,
            supplier_name='HealthTech Inc.'
        ),
    ]
    
    for item in inventory_items:
        db.session.add(item)
    
    db.session.commit()
    
    # Create some usage records
    items = InventoryItem.query.all()
    for item in items[:3]:  # Create usage for first 3 items
        usage = UsageRecord(
            item_id=item.id,
            usage_type='consumption',
            quantity=-5,  # Used 5 units
            notes='Daily usage',
            user_id=User.query.filter_by(role='nurse').first().id
        )
        db.session.add(usage)
    
    db.session.commit()

def create_sample_bills():
    """Create sample bills and payments."""
    patients = Patient.query.all()
    appointments = Appointment.query.filter_by(status='completed').all()
    
    for i, appointment in enumerate(appointments[:3]):
        # Create bill
        due_date = date.today() + timedelta(days=30)
        bill = Bill(
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            due_date=due_date,
            created_by=User.query.filter_by(role='receptionist').first().id
        )
        db.session.add(bill)
        db.session.flush()
        
        # Add bill items
        consultation_item = BillItem(
            bill_id=bill.id,
            description=f'Consultation - {appointment.appointment_type}',
            quantity=1,
            unit_price=appointment.consultation_fee,
            service_type='consultation'
        )
        db.session.add(consultation_item)
        
        # Add additional items
        if i == 0:
            lab_item = BillItem(
                bill_id=bill.id,
                description='Blood Test - Complete Blood Count',
                quantity=1,
                unit_price=50.00,
                service_type='lab_test'
            )
            db.session.add(lab_item)
        
        # Calculate total
        bill.calculate_total()
        
        # Create payment for some bills
        if i < 2:  # Pay first 2 bills
            payment = Payment(
                bill_id=bill.id,
                amount=bill.total_amount,
                payment_method='card',
                reference_number=f'TXN{1000 + i}',
                created_by=User.query.filter_by(role='receptionist').first().id
            )
            bill.add_payment(payment.amount, payment.payment_method, payment.reference_number)
    
    db.session.commit()

if __name__ == '__main__':
    init_database()