from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.billing import Bill, Payment, BillItem
from app.models.patient import Patient
from datetime import date, datetime, timedelta
from sqlalchemy import func

accountant_bp = Blueprint('accountant', __name__)

@accountant_bp.route('/dashboard')
@login_required
def dashboard():
    """Accountant dashboard."""
    if not current_user.can_manage_billing():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    today = date.today()
    
    # Financial statistics
    stats = {
        'total_bills': Bill.query.count(),
        'pending_bills': Bill.query.filter(
            Bill.status.in_(['pending', 'partially_paid'])
        ).count(),
        'overdue_bills': Bill.query.filter(
            Bill.due_date < today,
            Bill.status.in_(['pending', 'partially_paid'])
        ).count(),
        'today_revenue': db.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date == today
        ).scalar() or 0
    }
    
    # Recent bills
    recent_bills = Bill.query.order_by(Bill.created_at.desc()).limit(10).all()
    
    # Recent payments
    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(10).all()
    
    # Overdue bills
    overdue_bills = Bill.query.filter(
        Bill.due_date < today,
        Bill.status.in_(['pending', 'partially_paid'])
    ).order_by(Bill.due_date).limit(5).all()
    
    # Revenue chart data (last 7 days)
    revenue_data = []
    for i in range(7):
        check_date = today - timedelta(days=i)
        daily_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date == check_date
        ).scalar() or 0
        revenue_data.append({
            'date': check_date.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })
    revenue_data.reverse()
    
    return render_template('accountant/dashboard.html',
                         stats=stats,
                         recent_bills=recent_bills,
                         recent_payments=recent_payments,
                         overdue_bills=overdue_bills,
                         revenue_data=revenue_data)

@accountant_bp.route('/bills')
@login_required
def manage_bills():
    """Manage bills."""
    if not current_user.can_manage_billing():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    
    query = Bill.query
    
    if search:
        query = query.join(Patient).filter(
            db.or_(
                Bill.bill_number.ilike(f'%{search}%'),
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.patient_id.ilike(f'%{search}%')
            )
        )
    
    if status_filter:
        query = query.filter(Bill.status == status_filter)
    
    bills = query.order_by(Bill.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('accountant/manage_bills.html',
                         bills=bills,
                         search=search,
                         status_filter=status_filter)

@accountant_bp.route('/bills/<int:id>')
@login_required
def view_bill(id):
    """View bill details."""
    if not current_user.can_manage_billing():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    bill = Bill.query.get_or_404(id)
    return render_template('accountant/view_bill.html', bill=bill)

@accountant_bp.route('/bills/create', methods=['GET', 'POST'])
@login_required
def create_bill():
    """Create new bill."""
    if not current_user.can_manage_billing():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        due_date = request.form.get('due_date')
        
        if not all([patient_id, due_date]):
            flash('Patient and due date are required.', 'error')
            return render_template('accountant/create_bill.html')
        
        try:
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid due date format.', 'error')
            return render_template('accountant/create_bill.html')
        
        try:
            bill = Bill(
                patient_id=patient_id,
                due_date=due_date_obj,
                created_by=current_user.id
            )
            db.session.add(bill)
            db.session.commit()
            
            flash('Bill created successfully!', 'success')
            return redirect(url_for('accountant.view_bill', id=bill.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating bill. Please try again.', 'error')
    
    # Get patients for dropdown
    patients = Patient.query.filter(Patient.is_active == True).order_by(Patient.first_name).all()
    return render_template('accountant/create_bill.html', patients=patients)

@accountant_bp.route('/payments')
@login_required
def manage_payments():
    """Manage payments."""
    if not current_user.can_manage_billing():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date', '', type=str)
    method_filter = request.args.get('method', '', type=str)
    
    query = Payment.query
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Payment.payment_date == filter_date)
        except ValueError:
            pass
    
    if method_filter:
        query = query.filter(Payment.payment_method == method_filter)
    
    payments = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('accountant/manage_payments.html',
                         payments=payments,
                         date_filter=date_filter,
                         method_filter=method_filter)

@accountant_bp.route('/reports')
@login_required
def reports():
    """Financial reports."""
    if not current_user.can_view_reports():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    today = date.today()
    
    # Date range from request or default to last 30 days
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = today.strftime('%Y-%m-%d')
    
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Revenue statistics
    revenue_stats = db.session.query(
        func.sum(Payment.amount).label('total_revenue'),
        func.count(Payment.id).label('total_payments'),
        func.avg(Payment.amount).label('average_payment')
    ).filter(
        Payment.payment_date.between(start_date_obj, end_date_obj)
    ).first()
    
    # Payment method breakdown
    payment_methods = db.session.query(
        Payment.payment_method,
        func.sum(Payment.amount).label('total'),
        func.count(Payment.id).label('count')
    ).filter(
        Payment.payment_date.between(start_date_obj, end_date_obj)
    ).group_by(Payment.payment_method).all()
    
    # Outstanding bills
    outstanding_bills = db.session.query(
        func.sum(Bill.total_amount - Bill.paid_amount).label('total_outstanding'),
        func.count(Bill.id).label('bills_count')
    ).filter(
        Bill.status.in_(['pending', 'partially_paid'])
    ).first()
    
    return render_template('accountant/reports.html',
                         revenue_stats=revenue_stats,
                         payment_methods=payment_methods,
                         outstanding_bills=outstanding_bills,
                         start_date=start_date,
                         end_date=end_date)