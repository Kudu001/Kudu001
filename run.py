import os
from app import create_app, db
from app.models.user import User
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.billing import Bill, Payment
from app.models.inventory import InventoryItem, UsageRecord

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.before_first_request
def create_tables():
    """Create database tables on first request."""
    db.create_all()

@app.shell_context_processor
def make_shell_context():
    """Make models available in shell context."""
    return {
        'db': db,
        'User': User,
        'Patient': Patient,
        'Appointment': Appointment,
        'Staff': Staff,
        'Bill': Bill,
        'Payment': Payment,
        'InventoryItem': InventoryItem,
        'UsageRecord': UsageRecord
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)