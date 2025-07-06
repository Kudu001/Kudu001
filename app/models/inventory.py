from datetime import datetime, date, timedelta
from app import db

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.Enum('Medication', 'Equipment', 'Supplies', 'Surgical', 'Laboratory', 'Emergency', name='item_categories'), nullable=False)
    description = db.Column(db.Text)
    
    # Quantity and Stock
    current_stock = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=10)
    maximum_stock = db.Column(db.Integer, default=100)
    unit_of_measure = db.Column(db.String(20), default='pieces')
    
    # Pricing
    unit_cost = db.Column(db.Decimal(10, 2), default=0.0)
    selling_price = db.Column(db.Decimal(10, 2), default=0.0)
    
    # Supplier Information
    supplier_name = db.Column(db.String(200))
    supplier_contact = db.Column(db.String(100))
    
    # Dates and Expiry
    expiry_date = db.Column(db.Date)
    last_restocked = db.Column(db.Date)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    requires_prescription = db.Column(db.Boolean, default=False)
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    usage_records = db.relationship('UsageRecord', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    reorder_requests = db.relationship('ReorderRequest', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_items')
    
    def __init__(self, name, category, current_stock=0, **kwargs):
        self.name = name
        self.category = category
        self.current_stock = current_stock
        self.item_code = self.generate_item_code()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_item_code(self):
        """Generate unique item code based on category."""
        category_codes = {
            'Medication': 'MED',
            'Equipment': 'EQP',
            'Supplies': 'SUP',
            'Surgical': 'SUR',
            'Laboratory': 'LAB',
            'Emergency': 'EMR'
        }
        
        cat_code = category_codes.get(self.category, 'ITM')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f'{cat_code}{timestamp}'
    
    @property
    def is_low_stock(self):
        """Check if item is below minimum stock level."""
        return self.current_stock <= self.minimum_stock
    
    @property
    def is_out_of_stock(self):
        """Check if item is out of stock."""
        return self.current_stock <= 0
    
    @property
    def is_expired(self):
        """Check if item is expired."""
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
    def is_expiring_soon(self, days=30):
        """Check if item is expiring within specified days."""
        if self.days_until_expiry is not None:
            return 0 < self.days_until_expiry <= days
        return False
    
    @property
    def stock_value(self):
        """Calculate total stock value."""
        return self.current_stock * self.unit_cost
    
    def add_stock(self, quantity, notes=None, user_id=None):
        """Add stock to inventory."""
        if quantity > 0:
            self.current_stock += quantity
            self.last_restocked = date.today()
            
            # Create usage record
            usage = UsageRecord(
                item_id=self.id,
                usage_type='restock',
                quantity=quantity,
                notes=notes,
                user_id=user_id
            )
            db.session.add(usage)
            db.session.commit()
            return True
        return False
    
    def use_stock(self, quantity, usage_type='consumption', notes=None, user_id=None):
        """Use stock from inventory."""
        if quantity > 0 and self.current_stock >= quantity:
            self.current_stock -= quantity
            
            # Create usage record
            usage = UsageRecord(
                item_id=self.id,
                usage_type=usage_type,
                quantity=-quantity,  # Negative for usage
                notes=notes,
                user_id=user_id
            )
            db.session.add(usage)
            
            # Check if reorder is needed
            if self.is_low_stock:
                self.create_reorder_request()
            
            db.session.commit()
            return True
        return False
    
    def create_reorder_request(self):
        """Create reorder request if not already exists."""
        existing_request = ReorderRequest.query.filter(
            ReorderRequest.item_id == self.id,
            ReorderRequest.status == 'pending'
        ).first()
        
        if not existing_request:
            reorder = ReorderRequest(
                item_id=self.id,
                requested_quantity=self.maximum_stock - self.current_stock,
                reason=f'Low stock alert: Current stock ({self.current_stock}) below minimum ({self.minimum_stock})'
            )
            db.session.add(reorder)
            return reorder
        return existing_request
    
    def get_usage_history(self, days=30):
        """Get usage history for specified days."""
        start_date = date.today() - timedelta(days=days)
        return self.usage_records.filter(
            UsageRecord.created_at >= start_date
        ).order_by(UsageRecord.created_at.desc())
    
    def calculate_consumption_rate(self, days=30):
        """Calculate average daily consumption rate."""
        history = self.get_usage_history(days)
        total_used = sum(abs(record.quantity) for record in history if record.quantity < 0)
        return total_used / days if days > 0 else 0
    
    def estimate_days_until_stockout(self):
        """Estimate days until stock runs out based on consumption rate."""
        consumption_rate = self.calculate_consumption_rate()
        if consumption_rate > 0:
            return self.current_stock / consumption_rate
        return None
    
    def to_dict(self):
        """Convert inventory item to dictionary."""
        return {
            'id': self.id,
            'item_code': self.item_code,
            'name': self.name,
            'category': self.category,
            'current_stock': self.current_stock,
            'minimum_stock': self.minimum_stock,
            'unit_of_measure': self.unit_of_measure,
            'unit_cost': float(self.unit_cost) if self.unit_cost else 0,
            'selling_price': float(self.selling_price) if self.selling_price else 0,
            'is_low_stock': self.is_low_stock,
            'is_out_of_stock': self.is_out_of_stock,
            'is_expired': self.is_expired,
            'days_until_expiry': self.days_until_expiry,
            'stock_value': float(self.stock_value) if self.stock_value else 0,
            'supplier_name': self.supplier_name
        }
    
    def __repr__(self):
        return f'<InventoryItem {self.item_code}: {self.name}>'

class UsageRecord(db.Model):
    __tablename__ = 'usage_records'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    usage_type = db.Column(db.Enum('consumption', 'restock', 'adjustment', 'waste', 'transfer', name='usage_types'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Positive for add, negative for use
    notes = db.Column(db.Text)
    reference_id = db.Column(db.String(50))  # Reference to appointment, bill, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    user = db.relationship('User', backref='usage_records')
    
    def __init__(self, item_id, usage_type, quantity, **kwargs):
        self.item_id = item_id
        self.usage_type = usage_type
        self.quantity = quantity
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert usage record to dictionary."""
        return {
            'id': self.id,
            'item_name': self.item.name if self.item else '',
            'usage_type': self.usage_type,
            'quantity': self.quantity,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.user.username if self.user else ''
        }
    
    def __repr__(self):
        return f'<UsageRecord {self.item.name if self.item else "Unknown"}: {self.quantity}>'

class ReorderRequest(db.Model):
    __tablename__ = 'reorder_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    requested_quantity = db.Column(db.Integer, nullable=False)
    approved_quantity = db.Column(db.Integer)
    priority = db.Column(db.Enum('low', 'medium', 'high', 'urgent', name='priority_levels'), default='medium')
    status = db.Column(db.Enum('pending', 'approved', 'ordered', 'received', 'cancelled', name='reorder_status'), default='pending')
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Dates
    requested_date = db.Column(db.Date, default=date.today)
    expected_delivery = db.Column(db.Date)
    approved_date = db.Column(db.Date)
    
    # Cost
    estimated_cost = db.Column(db.Decimal(10, 2))
    actual_cost = db.Column(db.Decimal(10, 2))
    
    # System fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_reorder_requests')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_reorder_requests')
    
    def __init__(self, item_id, requested_quantity, **kwargs):
        self.item_id = item_id
        self.requested_quantity = requested_quantity
        self.request_id = self.generate_request_id()
        
        # Calculate estimated cost
        if self.item and self.item.unit_cost:
            self.estimated_cost = self.item.unit_cost * requested_quantity
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_request_id(self):
        """Generate unique request ID."""
        date_str = date.today().strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        return f'REQ{date_str}{timestamp}'
    
    def approve(self, approved_quantity=None, approver_id=None):
        """Approve the reorder request."""
        self.status = 'approved'
        self.approved_quantity = approved_quantity or self.requested_quantity
        self.approved_date = date.today()
        self.approved_by = approver_id
        db.session.commit()
    
    def cancel(self, reason=None):
        """Cancel the reorder request."""
        self.status = 'cancelled'
        if reason:
            self.notes = f"{self.notes}\nCancelled: {reason}" if self.notes else f"Cancelled: {reason}"
        db.session.commit()
    
    def mark_ordered(self, expected_delivery=None):
        """Mark as ordered."""
        self.status = 'ordered'
        if expected_delivery:
            self.expected_delivery = expected_delivery
        db.session.commit()
    
    def mark_received(self, actual_quantity=None, actual_cost=None):
        """Mark as received and update inventory."""
        self.status = 'received'
        if actual_cost:
            self.actual_cost = actual_cost
        
        # Add stock to inventory
        quantity_to_add = actual_quantity or self.approved_quantity or self.requested_quantity
        if self.item:
            self.item.add_stock(quantity_to_add, f"Reorder received - Request ID: {self.request_id}")
        
        db.session.commit()
    
    def to_dict(self):
        """Convert reorder request to dictionary."""
        return {
            'id': self.id,
            'request_id': self.request_id,
            'item_name': self.item.name if self.item else '',
            'item_code': self.item.item_code if self.item else '',
            'requested_quantity': self.requested_quantity,
            'approved_quantity': self.approved_quantity,
            'priority': self.priority,
            'status': self.status,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'expected_delivery': self.expected_delivery.isoformat() if self.expected_delivery else None,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else 0,
            'reason': self.reason
        }
    
    def __repr__(self):
        return f'<ReorderRequest {self.request_id}: {self.item.name if self.item else "Unknown"}>'