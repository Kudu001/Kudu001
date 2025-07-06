from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.billing import Bill, Payment, BillItem
from app.models.patient import Patient
from app.models.appointment import Appointment
from datetime import date, datetime
from sqlalchemy import func
from decimal import Decimal

accountant_bp = Blueprint('accountant', __name__)

def accountant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'accountant':
            flash('Access denied. Accountant privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@accountant_bp.route('/dashboard')
@login_required
@accountant_required
def dashboard():
    """Accountant dashboard."""
    today = date.today()
    
    # Financial statistics
    total_revenue = db.session.query(func.sum(Payment.amount)).scalar() or 0
    pending_bills = Bill.query.filter(Bill.status == 'pending').count()
    overdue_bills = Bill.query.filter(
        Bill.due_date < today,
        Bill.status.in_(['pending', 'partial'])
    ).count()
    
    # Recent payments
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    
    # Outstanding amounts
    total_outstanding = db.session.query(
        func.sum(Bill.total_amount - Bill.paid_amount)
    ).filter(Bill.status != 'paid').scalar() or 0
    
    return render_template('accountant/dashboard.html',
                         total_revenue=total_revenue,
                         pending_bills=pending_bills,
                         overdue_bills=overdue_bills,
                         recent_payments=recent_payments,
                         total_outstanding=total_outstanding)

@accountant_bp.route('/bills')
@login_required
@accountant_required
def bills():
    """Manage bills."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Bill.query
    
    if status:
        query = query.filter(Bill.status == status)
    
    bills = query.order_by(Bill.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('accountant/bills.html',
                         bills=bills,
                         selected_status=status)

@accountant_bp.route('/bills/new', methods=['GET', 'POST'])
@login_required
@accountant_required
def create_bill():
    """Create new bill."""
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        appointment_id = request.form.get('appointment_id')
        
        bill = Bill(
            patient_id=patient_id,
            appointment_id=appointment_id if appointment_id else None,
            created_by=current_user.id
        )
        
        db.session.add(bill)
        db.session.commit()
        
        flash('Bill created successfully.', 'success')
        return redirect(url_for('accountant.bill_detail', bill_id=bill.id))
    
    patients = Patient.query.filter(Patient.is_active == True).order_by(Patient.first_name).all()
    return render_template('accountant/create_bill.html', patients=patients)

@accountant_bp.route('/bills/<int:bill_id>')
@login_required
@accountant_required
def bill_detail(bill_id):
    """View bill details."""
    bill = Bill.query.get_or_404(bill_id)
    return render_template('accountant/bill_detail.html', bill=bill)

@accountant_bp.route('/bills/<int:bill_id>/add_payment', methods=['POST'])
@login_required
@accountant_required
def add_payment(bill_id):
    """Add payment to bill."""
    bill = Bill.query.get_or_404(bill_id)
    amount = float(request.form.get('amount'))
    payment_method = request.form.get('payment_method')
    reference_number = request.form.get('reference_number')
    notes = request.form.get('notes')
    
    try:
        payment = bill.add_payment(
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes
        )
        flash(f'Payment of ${amount} added successfully.', 'success')
    except Exception as e:
        flash(f'Error adding payment: {str(e)}', 'error')
    
    return redirect(url_for('accountant.bill_detail', bill_id=bill_id))

@accountant_bp.route('/payments')
@login_required
@accountant_required
def payments():
    """View payments."""
    page = request.args.get('page', 1, type=int)
    payments = Payment.query.order_by(Payment.payment_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('accountant/payments.html', payments=payments)

@accountant_bp.route('/reports')
@login_required
@accountant_required
def reports():
    """Financial reports."""
    # Revenue statistics
    total_revenue = db.session.query(func.sum(Payment.amount)).scalar() or 0
    this_month_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.payment_date >= date.today().replace(day=1)
    ).scalar() or 0
    
    # Bill statistics
    total_bills = Bill.query.count()
    paid_bills = Bill.query.filter(Bill.status == 'paid').count()
    pending_bills = Bill.query.filter(Bill.status == 'pending').count()
    
    return render_template('accountant/reports.html',
                         total_revenue=total_revenue,
                         this_month_revenue=this_month_revenue,
                         total_bills=total_bills,
                         paid_bills=paid_bills,
                         pending_bills=pending_bills)