from flask import Blueprint, render_template, request, redirect, session, flash
from db import get_db
from controllers.security import hash_password
from controllers.settings import get_settings, save_settings
import datetime

extras_bp = Blueprint('extras', __name__)

@extras_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    conn = get_db()
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        desc = request.form.get('description')
        if not name:
            conn.close()
            flash('Category name is required.', 'error')
            return redirect('/ui/categories')
        try:
            conn.execute('INSERT INTO categories (name, description) VALUES (?, ?)', (name, desc))
            conn.commit()
            flash('Category "%s" added.' % name, 'success')
        except Exception:
            conn.rollback()
            flash('That category already exists.', 'error')
        conn.close()
        return redirect('/ui/categories')
    cats = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return render_template('generic_list.html', title='Categories', items=cats,
                           form_action='/ui/categories', fields=['name', 'description'],
                           description='Group medicines into categories for reporting and filtering.',
                           labels={'name': 'Category name', 'description': 'Description (optional)'},
                           optional=['description'])

@extras_bp.route('/users', methods=['GET', 'POST'])
def users():
    conn = get_db()
    if request.method == 'POST':
        user = (request.form.get('username') or '').strip()
        pwd = request.form.get('password')
        role = request.form.get('role') or 'Staff'
        if not user or not pwd:
            conn.close()
            flash('Username and password are required.', 'error')
            return redirect('/ui/users')
        try:
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                         (user, hash_password(pwd), role))
            conn.commit()
            flash('User "%s" created.' % user, 'success')
        except Exception:
            conn.rollback()
            flash('That username is already taken.', 'error')
        conn.close()
        return redirect('/ui/users')
    usr = conn.execute('SELECT id, username, role FROM users').fetchall()
    conn.close()
    return render_template('generic_list.html', title='Users', items=usr,
                           form_action='/ui/users', fields=['username', 'password', 'role'],
                           description='Staff accounts that can sign in to the system.',
                           labels={'username': 'Username', 'password': 'Password', 'role': 'Role'},
                           field_types={'password': 'password'},
                           selects={'role': [('Admin', 'Admin'), ('Staff', 'Staff'), ('Cashier', 'Cashier')]})

@extras_bp.route('/purchases', methods=['GET', 'POST'])
def purchases():
    conn = get_db()
    error = None

    if request.method == 'POST':
        supplier_raw = (request.form.get('supplier_id') or '').strip()
        medicine_raw = (request.form.get('medicine_id') or '').strip()
        quantity_raw = (request.form.get('quantity') or '').strip()

        supplier_id = None
        medicine_id = None
        quantity = None

        if supplier_raw:
            try:
                supplier_id = int(supplier_raw)
            except ValueError:
                error = 'Supplier must be selected from the list.'
            else:
                supplier = conn.execute('SELECT id FROM suppliers WHERE id = ?', (supplier_id,)).fetchone()
                if not supplier:
                    error = 'Supplier not found.'
        if error is None and not medicine_raw:
            error = 'Medicine is required.'
        elif error is None:
            try:
                medicine_id = int(medicine_raw)
            except ValueError:
                error = 'Medicine must be selected from the list.'
        if error is None:
            try:
                quantity = int(quantity_raw)
            except ValueError:
                error = 'Quantity must be a whole number.'
            else:
                if quantity <= 0:
                    error = 'Quantity must be at least 1.'

        medicine = None
        if error is None:
            medicine = conn.execute('SELECT id, medicine_name, cost_price FROM medicines WHERE id = ?', (medicine_id,)).fetchone()
            if not medicine:
                error = 'Medicine not found.'

        if error is None:
            unit_cost = medicine['cost_price']
            total = round(unit_cost * quantity, 2)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                cursor = conn.execute(
                    'INSERT INTO purchases (supplier_id, date_time, total_amount, status) VALUES (?, ?, ?, ?)',
                    (supplier_id, now, total, 'Received'))
                purchase_id = cursor.lastrowid
                conn.execute(
                    'INSERT INTO purchase_items (purchase_id, medicine_id, quantity, unit_cost, subtotal) VALUES (?, ?, ?, ?, ?)',
                    (purchase_id, medicine_id, quantity, unit_cost, total))
                # Receiving stock puts the units on the shelf.
                conn.execute('UPDATE medicines SET current_stock = current_stock + ? WHERE id = ?',
                             (quantity, medicine_id))
                conn.commit()
            except Exception:
                conn.rollback()
                error = 'Could not save the purchase.'
            else:
                conn.close()
                flash('Received %d unit(s) of %s — stock updated.' % (quantity, medicine['medicine_name']), 'success')
                return redirect('/ui/purchases')

    items = conn.execute('''
        SELECT p.*, s.supplier_name,
               COALESCE(GROUP_CONCAT(m.medicine_name || ' x' || pi.quantity, ', '), '') AS item_summary
        FROM purchases p
        LEFT JOIN suppliers s ON s.id = p.supplier_id
        LEFT JOIN purchase_items pi ON pi.purchase_id = p.id
        LEFT JOIN medicines m ON m.id = pi.medicine_id
        GROUP BY p.id
        ORDER BY p.id DESC
    ''').fetchall()
    medicines = conn.execute(
        'SELECT id, medicine_name, current_stock, cost_price FROM medicines ORDER BY medicine_name').fetchall()
    suppliers = conn.execute('SELECT id, supplier_name FROM suppliers ORDER BY supplier_name').fetchall()
    conn.close()
    return render_template('purchases.html', items=items, medicines=medicines,
                           suppliers=suppliers, error=error)

@extras_bp.route('/adjustments', methods=['GET', 'POST'])
def adjustments():
    conn = get_db()
    if request.method == 'POST':
        med_raw = (request.form.get('medicine_id') or '').strip()
        qty_raw = (request.form.get('qty') or '').strip()
        rsn = (request.form.get('reason') or '').strip()

        medicine_id = None
        qty = None
        error = None

        if not med_raw:
            error = 'Medicine is required.'
        else:
            try:
                medicine_id = int(med_raw)
            except ValueError:
                error = 'Medicine must be selected from the list.'
        if error is None:
            try:
                qty = int(qty_raw)
            except ValueError:
                error = 'Quantity must be a whole number (use a negative number to remove stock).'
        if error is None and qty == 0:
            error = 'Quantity cannot be zero.'
        if error is None and not conn.execute('SELECT id FROM medicines WHERE id = ?', (medicine_id,)).fetchone():
            error = 'Medicine not found.'

        if error:
            flash(error, 'error')
        else:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute('INSERT INTO adjustments (medicine_id, qty, reason, date_time) VALUES (?, ?, ?, ?)',
                         (medicine_id, qty, rsn, dt))
            # Update actual stock
            conn.execute('UPDATE medicines SET current_stock = current_stock + ? WHERE id = ?', (qty, medicine_id))
            conn.commit()
            flash('Stock adjusted by %+d units.' % qty, 'success')
        conn.close()
        return redirect('/ui/adjustments')
    adj = conn.execute(
        'SELECT a.id, COALESCE(m.medicine_name, a.medicine_id) AS medicine_name, '
        ' a.qty, a.reason, a.date_time '
        'FROM adjustments a LEFT JOIN medicines m ON m.id = a.medicine_id '
        'ORDER BY a.id DESC'
    ).fetchall()
    medicine_options = [(m['id'], m['medicine_name']) for m in
                        conn.execute('SELECT id, medicine_name FROM medicines ORDER BY medicine_name').fetchall()]
    conn.close()
    return render_template('generic_list.html', title='Stock Adjustments', items=adj,
                           form_action='/ui/adjustments', fields=['medicine_id', 'qty', 'reason'],
                           description='Correct stock counts after breakage, expiry or a physical count.',
                           labels={'medicine_id': 'Medicine', 'qty': 'Quantity change (+/−)',
                                   'reason': 'Reason'},
                           field_types={'qty': 'number'},
                           selects={'medicine_id': medicine_options})

@extras_bp.route('/reports')
def reports():
    conn = get_db()

    revenue = conn.execute('SELECT COALESCE(SUM(total_amount), 0) AS v FROM sales').fetchone()['v']
    purchases_total = conn.execute('SELECT COALESCE(SUM(total_amount), 0) AS v FROM purchases').fetchone()['v']

    # Cost of goods sold: line items x current cost price.
    cogs_row = conn.execute(
        'SELECT COALESCE(SUM(si.quantity * m.cost_price), 0) AS cogs, '
        ' COALESCE(SUM(si.quantity), 0) AS items '
        'FROM sale_items si JOIN medicines m ON m.id = si.medicine_id'
    ).fetchone()
    cogs = cogs_row['cogs']
    items_sold = cogs_row['items']

    backfilled = conn.execute(
        'SELECT COUNT(*) AS c FROM sales WHERE legacy = 1'
    ).fetchone()['c']

    # Revenue for the last 30 days, zero-filled.
    rows = conn.execute(
        "SELECT date(date_time) AS day, COALESCE(SUM(total_amount), 0) AS amount "
        "FROM sales WHERE date(date_time) >= date('now', '-29 days') "
        "GROUP BY day ORDER BY day"
    ).fetchall()
    by_day = {r['day']: r['amount'] for r in rows}
    chart_labels, chart_values = [], []
    for i in range(29, -1, -1):
        d = datetime.date.today() - datetime.timedelta(days=i)
        chart_labels.append(d.strftime('%b %d'))
        chart_values.append(round(by_day.get(d.isoformat(), 0), 2))

    top_medicines = conn.execute(
        'SELECT m.medicine_name, m.generic_name, '
        ' SUM(si.quantity * si.unit_price) AS revenue, SUM(si.quantity) AS qty '
        'FROM sale_items si JOIN medicines m ON m.id = si.medicine_id '
        'GROUP BY m.id ORDER BY revenue DESC LIMIT 5'
    ).fetchall()

    conn.close()

    gross_profit = revenue - cogs
    margin = (gross_profit / revenue * 100) if revenue else 0

    return render_template(
        'reports.html',
        sales=revenue,
        purchases=purchases_total,
        profit=gross_profit,
        cogs=cogs,
        margin=margin,
        items_sold=items_sold,
        legacy_sales=backfilled,
        chart_labels=chart_labels,
        chart_values=chart_values,
        top_medicines=[dict(r) for r in top_medicines],
    )

@extras_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        store_name = (request.form.get('store_name') or '').strip()
        currency = (request.form.get('currency') or '').strip()
        threshold_raw = (request.form.get('low_stock_threshold') or '').strip()
        invoice_prefix = (request.form.get('invoice_prefix') or '').strip()

        if not store_name:
            flash('Store name is required.', 'error')
            return redirect('/ui/settings')
        if not invoice_prefix:
            flash('Invoice prefix is required.', 'error')
            return redirect('/ui/settings')
        try:
            threshold = int(threshold_raw)
        except (TypeError, ValueError):
            threshold = 0
        if threshold < 1:
            flash('Low stock threshold must be a whole number of at least 1.', 'error')
            return redirect('/ui/settings')

        save_settings({
            'store_name': store_name,
            'currency': currency or u'\u20b1',
            'low_stock_threshold': str(threshold),
            'invoice_prefix': invoice_prefix,
        })

        # The threshold drives the derived stock status — re-sync it now.
        conn = get_db()
        conn.execute('''
            UPDATE medicines SET status = CASE
                WHEN current_stock <= 0 THEN 'Out of Stock'
                WHEN current_stock <= ? THEN 'Low Stock' ELSE 'In Stock' END
        ''', (threshold,))
        conn.commit()
        conn.close()

        flash('Settings saved.', 'success')
        return redirect('/ui/settings')
    return render_template('settings.html', settings=get_settings())
