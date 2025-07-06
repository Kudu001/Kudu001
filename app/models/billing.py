from datetime import datetime, date
from decimal import Decimal
from app import db

class Bill(db.Model):
    __tablename__ = 'bills'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    
    # Bill Details
    bill_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Decimal(10, 2), nullable=False, default=0.0)
    paid_amount = db.Column(db.Decimal(10, 2), default=0.0)
    discount_amount = db.Column(db.Decimal(10, 2), default=0.0)
    tax_amount = db.Column(db.Decimal(10, 2), default=0.0)
    
    # Status and Notes
    status = db.Column(db.Enum('draft', 'pending', 'paid', 'partially_paid', 'overdue', 'cancelled', name='bill_status'), default='pending')
    notes = db.Column(db.Text)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    bill_items = db.relationship('BillItem', backref='bill', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='bill', lazy='dynamic', cascade='all, delete-orphan')
    appointment = db.relationship('Appointment', backref='bills')
    creator = db.relationship('User', backref='created_bills')
    
    def __init__(self, patient_id, due_date, **kwargs):
        self.patient_id = patient_id
        self.due_date = due_date
        self.bill_number = self.generate_bill_number()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_bill_number(self):
        """Generate unique bill number."""
        date_str = date.today().strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        return f'BILL{date_str}{timestamp}'
    
    @property
    def outstanding_amount(self):
        """Calculate outstanding amount."""
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """Check if bill is overdue."""
        return date.today() > self.due_date and self.status not in ['paid', 'cancelled']
    
    @property
    def payment_percentage(self):
        """Calculate payment percentage."""
        if self.total_amount > 0:
            return (self.paid_amount / self.total_amount) * 100
        return 0
    
    def add_item(self, description, quantity, unit_price, service_type='consultation'):
        """Add item to bill."""
        item = BillItem(
            bill_id=self.id,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            service_type=service_type
        )
        db.session.add(item)
        self.calculate_total()
        return item
    
    def calculate_total(self):
        """Calculate total amount from all bill items."""
        total = sum(item.total_price for item in self.bill_items)
        self.total_amount = total + self.tax_amount - self.discount_amount
        
        # Update status based on payment
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partially_paid'
        elif self.is_overdue:
            self.status = 'overdue'
        else:
            self.status = 'pending'
        
        db.session.commit()
    
    def add_payment(self, amount, payment_method='cash', reference_number=None):
        """Add payment to bill."""
        if amount <= 0:
            return False
        
        payment = Payment(
            bill_id=self.id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number
        )
        db.session.add(payment)
        
        self.paid_amount += amount
        self.calculate_total()
        return payment
    
    def apply_discount(self, amount, reason=None):
        """Apply discount to bill."""
        self.discount_amount += amount
        if reason:
            self.notes = f"{self.notes}\nDiscount applied: {reason}" if self.notes else f"Discount applied: {reason}"
        self.calculate_total()
    
    def cancel(self, reason=None):
        """Cancel the bill."""
        self.status = 'cancelled'
        if reason:
            self.notes = f"{self.notes}\nCancelled: {reason}" if self.notes else f"Cancelled: {reason}"
        db.session.commit()
    
    def to_dict(self):
        """Convert bill to dictionary."""
        return {
            'id': self.id,
            'bill_number': self.bill_number,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else '',
            'bill_date': self.bill_date.isoformat() if self.bill_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'total_amount': float(self.total_amount),
            'paid_amount': float(self.paid_amount),
            'outstanding_amount': float(self.outstanding_amount),
            'status': self.status,
            'is_overdue': self.is_overdue,
            'payment_percentage': self.payment_percentage,
            'items': [item.to_dict() for item in self.bill_items]
        }
    
    def __repr__(self):
        return f'<Bill {self.bill_number}: {self.patient.full_name if self.patient else "Unknown"}>'

class BillItem(db.Model):
    __tablename__ = 'bill_items'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    service_type = db.Column(db.Enum('consultation', 'procedure', 'medication', 'lab_test', 'imaging', 'room_charge', 'other', name='service_types'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Decimal(10, 2), nullable=False)
    total_price = db.Column(db.Decimal(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, bill_id, description, quantity, unit_price, service_type='consultation'):
        self.bill_id = bill_id
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.service_type = service_type
        self.total_price = Decimal(str(quantity)) * Decimal(str(unit_price))
    
    def to_dict(self):
        """Convert bill item to dictionary."""
        return {
            'id': self.id,
            'description': self.description,
            'service_type': self.service_type,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        }
    
    def __repr__(self):
        return f'<BillItem {self.description}: {self.total_price}>'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    amount = db.Column(db.Decimal(10, 2), nullable=False)
    payment_date = db.Column(db.Date, default=date.today)
    payment_method = db.Column(db.Enum('cash', 'card', 'bank_transfer', 'insurance', 'cheque', name='payment_methods'), nullable=False)
    reference_number = db.Column(db.String(50))
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded', name='payment_status'), default='completed')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', backref='created_payments')
    
    def __init__(self, bill_id, amount, payment_method='cash', **kwargs):
        self.bill_id = bill_id
        self.amount = amount
        self.payment_method = payment_method
        self.payment_id = self.generate_payment_id()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_payment_id(self):
        """Generate unique payment ID."""
        date_str = date.today().strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        return f'PAY{date_str}{timestamp}'
    
    def refund(self, reason=None):
        """Refund the payment."""
        if self.status == 'completed':
            self.status = 'refunded'
            if reason:
                self.notes = f"{self.notes}\nRefunded: {reason}" if self.notes else f"Refunded: {reason}"
            
            # Update bill paid amount
            self.bill.paid_amount -= self.amount
            self.bill.calculate_total()
            db.session.commit()
            return True
        return False
    
    def to_dict(self):
        """Convert payment to dictionary."""
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'amount': float(self.amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'status': self.status,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Payment {self.payment_id}: {self.amount}>'