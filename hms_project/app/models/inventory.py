from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Numeric
from app import db

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.Enum('Medicine', 'Equipment', 'Supplies', 'Consumables', name='item_categories'), nullable=False)
    sub_category = db.Column(db.String(50))
    
    # Stock Information
    current_stock = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=10)
    maximum_stock = db.Column(db.Integer, default=1000)
    unit = db.Column(db.String(20), default='pieces')  # pieces, bottles, boxes, etc.
    
    # Pricing
    unit_price = db.Column(Numeric(10, 2), default=0.0)
    supplier_price = db.Column(Numeric(10, 2), default=0.0)
    
    # Medicine specific fields
    generic_name = db.Column(db.String(100))
    brand_name = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    dosage = db.Column(db.String(50))
    
    # Supplier Information
    supplier_name = db.Column(db.String(100))
    supplier_contact = db.Column(db.String(100))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    requires_prescription = db.Column(db.Boolean, default=False)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    usage_records = db.relationship('UsageRecord', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    stock_movements = db.relationship('StockMovement', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_inventory_items')
    
    def __init__(self, name, category, **kwargs):
        self.name = name
        self.category = category
        self.item_code = self.generate_item_code()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_item_code(self):
        """Generate unique item code."""
        import random
        category_codes = {
            'Medicine': 'MED',
            'Equipment': 'EQP',
            'Supplies': 'SUP',
            'Consumables': 'CON'
        }
        
        cat_code = category_codes.get(self.category, 'ITM')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = random.randint(100, 999)
        return f'{cat_code}{timestamp}{random_suffix}'
    
    @property
    def is_low_stock(self):
        """Check if item is low on stock."""
        return self.current_stock <= self.minimum_stock
    
    @property
    def is_out_of_stock(self):
        """Check if item is out of stock."""
        return self.current_stock <= 0
    
    @property
    def is_expired(self):
        """Check if item is expired (for medicines)."""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry."""
        if self.expiry_date:
            delta = self.expiry_date - date.today()
            return delta.days
        return None
    
    @property
    def stock_value(self):
        """Calculate current stock value."""
        return self.current_stock * self.unit_price
    
    def add_stock(self, quantity, reason='Stock Added', reference=None, user_id=None):
        """Add stock to inventory."""
        self.current_stock += quantity
        
        # Create stock movement record
        movement = StockMovement(
            item_id=self.id,
            movement_type='in',
            quantity=quantity,
            reason=reason,
            reference=reference,
            created_by=user_id
        )
        db.session.add(movement)
        db.session.commit()
        return movement
    
    def remove_stock(self, quantity, reason='Stock Used', reference=None, user_id=None):
        """Remove stock from inventory."""
        if self.current_stock >= quantity:
            self.current_stock -= quantity
            
            # Create stock movement record
            movement = StockMovement(
                item_id=self.id,
                movement_type='out',
                quantity=quantity,
                reason=reason,
                reference=reference,
                created_by=user_id
            )
            db.session.add(movement)
            db.session.commit()
            return movement
        else:
            raise ValueError("Insufficient stock available")
    
    def use_item(self, quantity, used_by_id, patient_id=None, notes=None):
        """Record usage of inventory item."""
        if self.current_stock >= quantity:
            # Create usage record
            usage = UsageRecord(
                item_id=self.id,
                quantity=quantity,
                used_by=used_by_id,
                patient_id=patient_id,
                notes=notes
            )
            db.session.add(usage)
            
            # Remove from stock
            self.remove_stock(quantity, f"Used by staff ID: {used_by_id}", user_id=used_by_id)
            return usage
        else:
            raise ValueError("Insufficient stock available")
    
    def reorder_needed(self):
        """Check if item needs reordering."""
        return self.is_low_stock and self.is_active
    
    def get_reorder_quantity(self):
        """Calculate recommended reorder quantity."""
        if self.reorder_needed():
            return self.maximum_stock - self.current_stock
        return 0
    
    def to_dict(self):
        """Convert item to dictionary."""
        return {
            'id': self.id,
            'item_code': self.item_code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'current_stock': self.current_stock,
            'minimum_stock': self.minimum_stock,
            'unit': self.unit,
            'unit_price': float(self.unit_price),
            'is_low_stock': self.is_low_stock,
            'is_out_of_stock': self.is_out_of_stock,
            'is_expired': self.is_expired,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'manufacturer': self.manufacturer,
            'batch_number': self.batch_number,
            'stock_value': float(self.stock_value)
        }
    
    def __repr__(self):
        return f'<InventoryItem {self.item_code}: {self.name}>'

class UsageRecord(db.Model):
    __tablename__ = 'usage_records'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    usage_date = db.Column(db.DateTime, default=datetime.utcnow)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='inventory_usage')
    patient = db.relationship('Patient', backref='inventory_used')
    
    def to_dict(self):
        """Convert usage record to dictionary."""
        return {
            'id': self.id,
            'item_name': self.item.name if self.item else '',
            'quantity': self.quantity,
            'usage_date': self.usage_date.isoformat() if self.usage_date else None,
            'used_by': self.user.username if self.user else '',
            'patient_name': self.patient.full_name if self.patient else '',
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<UsageRecord {self.item.name}: {self.quantity} units>'

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    movement_type = db.Column(db.Enum('in', 'out', 'adjustment', name='movement_types'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    reference = db.Column(db.String(100))  # PO number, invoice number, etc.
    movement_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='stock_movements')
    
    def to_dict(self):
        """Convert stock movement to dictionary."""
        return {
            'id': self.id,
            'item_name': self.item.name if self.item else '',
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'reason': self.reason,
            'reference': self.reference,
            'movement_date': self.movement_date.isoformat() if self.movement_date else None,
            'created_by': self.creator.username if self.creator else ''
        }
    
    def __repr__(self):
        return f'<StockMovement {self.item.name}: {self.movement_type} {self.quantity}>'