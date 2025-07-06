from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Numeric
from app import db

class Bill(db.Model):
    __tablename__ = 'bills'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    
    # Bill Details
    bill_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date)
    total_amount = db.Column(Numeric(10, 2), nullable=False, default=0.0)
    paid_amount = db.Column(Numeric(10, 2), default=0.0)
    discount_amount = db.Column(Numeric(10, 2), default=0.0)
    tax_amount = db.Column(Numeric(10, 2), default=0.0)
    
    # Status and Payment
    status = db.Column(db.Enum('pending', 'partial', 'paid', 'overdue', 'cancelled', name='bill_status'), default='pending')
    payment_method = db.Column(db.Enum('cash', 'card', 'insurance', 'bank_transfer', 'online', name='payment_methods'))
    
    # Additional Information
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bill_items = db.relationship('BillItem', backref='bill', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='bill', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_bills')
    appointment = db.relationship('Appointment', backref='bills')
    
    def __init__(self, patient_id, total_amount=0.0, **kwargs):
        self.patient_id = patient_id
        self.total_amount = Decimal(str(total_amount))
        self.bill_number = self.generate_bill_number()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_bill_number(self):
        """Generate unique bill number."""
        import random
        today = date.today()
        date_str = today.strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        random_suffix = random.randint(100, 999)
        return f'BILL{date_str}{timestamp}{random_suffix}'
    
    @property
    def outstanding_amount(self):
        """Calculate outstanding amount."""
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """Check if bill is overdue."""
        if self.due_date and self.status not in ['paid', 'cancelled']:
            return date.today() > self.due_date
        return False
    
    @property
    def payment_percentage(self):
        """Calculate payment percentage."""
        if self.total_amount > 0:
            return (self.paid_amount / self.total_amount) * 100
        return 0
    
    def add_item(self, description, quantity, unit_price, item_type='service'):
        """Add item to bill."""
        bill_item = BillItem(
            bill_id=self.id,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            item_type=item_type
        )
        db.session.add(bill_item)
        self.calculate_total()
        return bill_item
    
    def calculate_total(self):
        """Calculate total amount based on bill items."""
        items_total = sum(item.total_amount for item in self.bill_items)
        self.total_amount = items_total + self.tax_amount - self.discount_amount
        self.update_status()
    
    def update_status(self):
        """Update bill status based on payment."""
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        elif self.is_overdue:
            self.status = 'overdue'
        else:
            self.status = 'pending'
    
    def add_payment(self, amount, payment_method='cash', reference_number=None, notes=None):
        """Add payment to bill."""
        payment = Payment(
            bill_id=self.id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes
        )
        db.session.add(payment)
        
        # Update paid amount
        self.paid_amount += Decimal(str(amount))
        self.update_status()
        db.session.commit()
        return payment
    
    def apply_discount(self, discount_amount, reason=None):
        """Apply discount to bill."""
        self.discount_amount = Decimal(str(discount_amount))
        if reason:
            self.notes = f"{self.notes or ''}\nDiscount applied: {reason}"
        self.calculate_total()
        db.session.commit()
    
    def cancel(self, reason=None):
        """Cancel the bill."""
        self.status = 'cancelled'
        if reason:
            self.notes = f"{self.notes or ''}\nCancelled: {reason}"
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
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Bill {self.bill_number}: ${self.total_amount}>'

class BillItem(db.Model):
    __tablename__ = 'bill_items'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(Numeric(10, 2), nullable=False)
    item_type = db.Column(db.Enum('service', 'medication', 'test', 'procedure', 'consultation', name='bill_item_types'), default='service')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def total_amount(self):
        """Calculate total amount for this item."""
        return self.quantity * self.unit_price
    
    def __repr__(self):
        return f'<BillItem {self.description}: ${self.total_amount}>'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.Enum('cash', 'card', 'insurance', 'bank_transfer', 'online', name='payment_method_types'), nullable=False)
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded', name='payment_status'), default='completed')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='processed_payments')
    
    def __init__(self, bill_id, amount, payment_method='cash', **kwargs):
        self.bill_id = bill_id
        self.amount = Decimal(str(amount))
        self.payment_method = payment_method
        self.payment_id = self.generate_payment_id()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_payment_id(self):
        """Generate unique payment ID."""
        import random
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = random.randint(100, 999)
        return f'PAY{timestamp}{random_suffix}'
    
    def refund(self, reason=None):
        """Refund the payment."""
        self.status = 'refunded'
        if reason:
            self.notes = f"{self.notes or ''}\nRefunded: {reason}"
        
        # Update bill paid amount
        self.bill.paid_amount -= self.amount
        self.bill.update_status()
        db.session.commit()
    
    def to_dict(self):
        """Convert payment to dictionary."""
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'bill_id': self.bill_id,
            'amount': float(self.amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'status': self.status,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Payment {self.payment_id}: ${self.amount}>'