from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.patient import Patient
from app.models.inventory import InventoryItem, UsageRecord, ReorderRequest
from app.models.staff import Staff
from datetime import date, datetime, timedelta

nurse_bp = Blueprint('nurse', __name__)

@nurse_bp.route('/dashboard')
@login_required
def dashboard():
    """Nurse dashboard."""
    if not current_user.can_manage_inventory():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    today = date.today()
    
    # Inventory statistics
    stats = {
        'total_items': InventoryItem.query.filter(InventoryItem.is_active == True).count(),
        'low_stock_items': InventoryItem.query.filter(
            InventoryItem.current_stock <= InventoryItem.minimum_stock,
            InventoryItem.is_active == True
        ).count(),
        'out_of_stock': InventoryItem.query.filter(
            InventoryItem.current_stock <= 0,
            InventoryItem.is_active == True
        ).count(),
        'pending_reorders': ReorderRequest.query.filter(
            ReorderRequest.status == 'pending'
        ).count()
    }
    
    # Low stock alerts
    low_stock_items = InventoryItem.query.filter(
        InventoryItem.current_stock <= InventoryItem.minimum_stock,
        InventoryItem.is_active == True
    ).limit(10).all()
    
    # Recent usage
    recent_usage = UsageRecord.query.order_by(
        UsageRecord.created_at.desc()
    ).limit(10).all()
    
    # Pending reorder requests
    pending_reorders = ReorderRequest.query.filter(
        ReorderRequest.status == 'pending'
    ).order_by(ReorderRequest.created_at.desc()).limit(5).all()
    
    return render_template('nurse/dashboard.html',
                         stats=stats,
                         low_stock_items=low_stock_items,
                         recent_usage=recent_usage,
                         pending_reorders=pending_reorders)

@nurse_bp.route('/inventory')
@login_required
def inventory():
    """Manage inventory."""
    if not current_user.can_manage_inventory():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category_filter = request.args.get('category', '', type=str)
    stock_filter = request.args.get('stock', '', type=str)
    
    query = InventoryItem.query.filter(InventoryItem.is_active == True)
    
    if search:
        query = query.filter(
            db.or_(
                InventoryItem.name.ilike(f'%{search}%'),
                InventoryItem.item_code.ilike(f'%{search}%'),
                InventoryItem.description.ilike(f'%{search}%')
            )
        )
    
    if category_filter:
        query = query.filter(InventoryItem.category == category_filter)
    
    if stock_filter == 'low':
        query = query.filter(InventoryItem.current_stock <= InventoryItem.minimum_stock)
    elif stock_filter == 'out':
        query = query.filter(InventoryItem.current_stock <= 0)
    
    items = query.order_by(InventoryItem.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get categories for filter
    categories = db.session.query(InventoryItem.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('nurse/inventory.html',
                         items=items,
                         search=search,
                         category_filter=category_filter,
                         stock_filter=stock_filter,
                         categories=categories)

@nurse_bp.route('/inventory/<int:id>')
@login_required
def view_item(id):
    """View inventory item details."""
    if not current_user.can_manage_inventory():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    item = InventoryItem.query.get_or_404(id)
    
    # Get usage history
    usage_history = item.usage_records.order_by(
        UsageRecord.created_at.desc()
    ).limit(20).all()
    
    # Get reorder requests
    reorder_requests = item.reorder_requests.order_by(
        ReorderRequest.created_at.desc()
    ).limit(5).all()
    
    return render_template('nurse/view_item.html',
                         item=item,
                         usage_history=usage_history,
                         reorder_requests=reorder_requests)

@nurse_bp.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_item():
    """Add new inventory item."""
    if not current_user.can_manage_inventory():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description', '')
        current_stock = request.form.get('current_stock', 0, type=int)
        minimum_stock = request.form.get('minimum_stock', 10, type=int)
        maximum_stock = request.form.get('maximum_stock', 100, type=int)
        unit_of_measure = request.form.get('unit_of_measure', 'pieces')
        unit_cost = request.form.get('unit_cost', 0.0, type=float)
        supplier_name = request.form.get('supplier_name', '')
        
        if not all([name, category]):
            flash('Name and category are required.', 'error')
            return render_template('nurse/add_item.html')
        
        try:
            item = InventoryItem(
                name=name,
                category=category,
                description=description,
                current_stock=current_stock,
                minimum_stock=minimum_stock,
                maximum_stock=maximum_stock,
                unit_of_measure=unit_of_measure,
                unit_cost=unit_cost,
                supplier_name=supplier_name,
                created_by=current_user.id
            )
            db.session.add(item)
            db.session.commit()
            
            flash(f'Item {name} added successfully!', 'success')
            return redirect(url_for('nurse.view_item', id=item.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error adding item. Please try again.', 'error')
    
    return render_template('nurse/add_item.html')

@nurse_bp.route('/patients')
@login_required
def patients():
    """View patients for nursing care."""
    if not current_user.can_manage_patients():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Patient.query.filter(Patient.is_active == True)
    
    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.patient_id.ilike(f'%{search}%')
            )
        )
    
    patients = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('nurse/patients.html', patients=patients, search=search)