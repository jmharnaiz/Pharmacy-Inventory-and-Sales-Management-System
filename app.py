import os
import secrets
from math import ceil
from datetime import date, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from routes.medicines import medicines_bp
from routes.customers import customers_bp
from routes.suppliers import suppliers_bp
from routes.sales import sales_bp
from routes.extras import extras_bp
from controllers.medicines import (
    get_all_medicines, get_medicine_by_id, search_medicines,
    list_categories, LOW_STOCK_THRESHOLD,
)
from controllers.customers import get_all_customers, get_customer_by_id, search_customers
from controllers.suppliers import get_supplier_by_id, search_suppliers
from controllers.sales import get_sale_by_id, search_sales, get_sale_items
from controllers.security import check_password
from controllers.settings import get_setting, int_setting
from db import ensure_schema, get_db

app = Flask(__name__)


def _load_secret_key():
    """Secret key from the environment, or a persisted generated value.

    A random key is generated once and saved to `.secret_key` so sessions
    survive restarts in development, while `SECRET_KEY` in the environment
    wins in any real deployment. On serverless (Vercel) the filesystem is
    read-only, so `SECRET_KEY` must be provided there; without it the key
    changes every cold start and users just get signed out.
    """
    env_key = os.environ.get('SECRET_KEY')
    if env_key:
        return env_key
    if os.environ.get('VERCEL') == '1':
        return secrets.token_hex(32)
    key_path = os.path.join(os.path.dirname(__file__), '.secret_key')
    if os.path.exists(key_path):
        with open(key_path) as fh:
            persisted = fh.read().strip()
        if persisted:
            return persisted
    key = secrets.token_hex(32)
    try:
        with open(key_path, 'w') as fh:
            fh.write(key)
    except OSError:
        pass
    return key


app.secret_key = _load_secret_key()

# Creates any tables added since the database file was generated (idempotent).
ensure_schema()

app.register_blueprint(medicines_bp, url_prefix='/api/medicines')
app.register_blueprint(customers_bp, url_prefix='/api/customers')
app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
app.register_blueprint(sales_bp, url_prefix='/api/sales')
app.register_blueprint(extras_bp, url_prefix='/ui')

PER_PAGE = 10

LOGIN_EXEMPT_ENDPOINTS = {'login', 'static'}


@app.before_request
def ensure_csrf_token():
    """Give every visitor a CSRF token so rendered forms always have one."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)


@app.before_request
def require_login():
    """Protect every page and API endpoint behind a session.

    Having no session is a redirect for the UI and a 401 for API calls.
    """
    if app.config.get('TESTING'):
        return None
    if request.endpoint in LOGIN_EXEMPT_ENDPOINTS:
        return None
    if 'user' not in session:
        if request.path.startswith('/api/'):
            return jsonify({"status": 401, "error": "Authentication required. Please sign in."}), 401
        return redirect('/login')


@app.before_request
def csrf_protect():
    """Reject state-changing requests without a valid CSRF token."""
    if app.config.get('TESTING'):
        return None
    if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
        return None
    submitted = request.form.get('csrf_token') or request.headers.get('X-CSRFToken') or ''
    if not submitted or submitted != session.get('csrf_token'):
        if request.path.startswith('/api/'):
            return jsonify({"status": 400, "error": "Missing or invalid CSRF token. Reload the page and try again."}), 400
        flash('Your form session expired — please try again.', 'error')
        return redirect(request.referrer or '/')


@app.context_processor
def inject_globals():
    """Store preferences + CSRF token available to every template."""
    return {
        'store_name': get_setting('store_name'),
        'currency': get_setting('currency'),
        'low_stock_threshold': int_setting('low_stock_threshold', LOW_STOCK_THRESHOLD),
        'csrf_token': session.get('csrf_token', ''),
    }


@app.context_processor
def inject_stock_alerts():
    """Low/out-of-stock counts for the header bell badge and sidebar."""
    threshold = int_setting('low_stock_threshold', LOW_STOCK_THRESHOLD)
    conn = get_db()
    row = conn.execute(
        'SELECT '
        ' SUM(CASE WHEN current_stock = 0 THEN 1 ELSE 0 END) AS out_count, '
        ' SUM(CASE WHEN current_stock > 0 AND current_stock <= ? THEN 1 ELSE 0 END) AS low_count '
        'FROM medicines',
        (threshold,)
    ).fetchone()
    conn.close()
    out_count = row['out_count'] or 0
    low_count = row['low_count'] or 0
    return {
        'stock_alerts': out_count + low_count,
        'out_of_stock_count': out_count,
        'low_stock_count': low_count,
    }


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = (request.form.get('username') or '').strip()
        pwd = request.form.get('password') or ''
        conn = get_db()
        u = conn.execute('SELECT * FROM users WHERE username = ?', (user,)).fetchone()
        conn.close()
        if u and check_password(u['password'], pwd):
            session['user'] = user
            session['role'] = u['role']
            flash('Welcome back, %s!' % user.title())
            return redirect('/')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.')
    return redirect('/login')


# --- Pagination helpers -------------------------------------------------------

def _page_base():
    """Current URL without the `page` param, e.g. `/ui/medicines?q=abc&`."""
    from urllib.parse import urlencode
    pairs = [(k, v) for k, v in request.args.items(multi=True) if k != 'page']
    return request.path + ('?' + urlencode(pairs) + '&' if pairs else '?')


def _paginate(page, total, per_page=PER_PAGE):
    pages = max(1, ceil((total or 0) / per_page))
    page = min(max(page or 1, 1), pages)
    return {'page': page, 'pages': pages, 'total': total,
            'per_page': per_page, 'page_base': _page_base()}


@app.route('/')
def dashboard():
    conn = get_db()
    threshold = int_setting('low_stock_threshold', LOW_STOCK_THRESHOLD)

    totals = conn.execute(
        'SELECT '
        ' (SELECT COUNT(*) FROM medicines) AS total_medicines, '
        ' (SELECT COALESCE(SUM(cost_price * current_stock), 0) FROM medicines) AS stock_value, '
        ' (SELECT COALESCE(SUM(total_amount), 0) FROM sales) AS total_sales, '
        ' (SELECT COUNT(*) FROM customers) AS total_customers, '
        ' (SELECT COALESCE(SUM(total_amount), 0) FROM sales '
        '  WHERE date(date_time) = date(\'now\')) AS sales_today, '
        ' (SELECT COUNT(*) FROM sales WHERE date(date_time) = date(\'now\')) AS sales_today_count'
    ).fetchone()

    # Sales for the last 7 days (zero-filled so the chart has a full week).
    rows = conn.execute(
        "SELECT date(date_time) AS day, COALESCE(SUM(total_amount), 0) AS amount "
        "FROM sales WHERE date(date_time) >= date('now', '-6 days') "
        "GROUP BY day ORDER BY day"
    ).fetchall()
    by_day = {r['day']: r['amount'] for r in rows}
    chart_labels, chart_values = [], []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        key = d.isoformat()
        chart_labels.append(d.strftime('%b %d'))
        chart_values.append(round(by_day.get(key, 0), 2))

    # Stock distribution across categories (top 6).
    cats = conn.execute(
        "SELECT COALESCE(NULLIF(category, ''), 'Uncategorized') AS cat, "
        " SUM(current_stock) AS units FROM medicines "
        " GROUP BY cat ORDER BY units DESC LIMIT 6"
    ).fetchall()

    recent_sales = conn.execute(
        'SELECT sales.*, customers.customer_name '
        'FROM sales LEFT JOIN customers ON customers.id = sales.customer_id '
        'ORDER BY sales.date_time DESC LIMIT 5'
    ).fetchall()

    low_stock = conn.execute(
        'SELECT * FROM medicines WHERE current_stock <= ? '
        'ORDER BY current_stock ASC LIMIT 6',
        (threshold,)
    ).fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        total_medicines=totals['total_medicines'],
        total_stock_value=totals['stock_value'],
        total_sales=totals['total_sales'],
        total_customers=totals['total_customers'],
        sales_today=totals['sales_today'],
        sales_today_count=totals['sales_today_count'],
        chart_labels=chart_labels,
        chart_values=chart_values,
        category_labels=[c['cat'] for c in cats],
        category_units=[c['units'] for c in cats],
        recent_sales=[dict(r) for r in recent_sales],
        low_stock=[dict(r) for r in low_stock],
    )

@app.route('/ui/medicines')
def ui_medicines_list():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', '').strip()
    page = request.args.get('page', 1, type=int) or 1

    medicines, total = search_medicines(q=q, category=category, sort=sort,
                                        page=page, per_page=PER_PAGE)
    pager = _paginate(page, total)
    return render_template('medicines_list.html', medicines=medicines,
                           q=q, category=category, sort=sort,
                           categories=list_categories(), pager=pager)

@app.route('/ui/medicines/new')
def ui_medicines_new():
    return render_template('medicine_form.html', medicine=None)

@app.route('/ui/medicines/<int:id>/edit')
def ui_medicines_edit(id):
    medicine = get_medicine_by_id(id)
    if not medicine:
        return render_template('medicine_form.html', error="Medicine not found")
    return render_template('medicine_form.html', medicine=medicine)

# Customers UI
@app.route('/ui/customers')
def ui_customers_list():
    q = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()
    sort = request.args.get('sort', '').strip()
    page = request.args.get('page', 1, type=int) or 1

    customers, total = search_customers(q=q, status=status, sort=sort,
                                        page=page, per_page=PER_PAGE)
    pager = _paginate(page, total)
    return render_template('customers_list.html', customers=customers,
                           q=q, status=status, sort=sort, pager=pager)

@app.route('/ui/customers/new')
def ui_customers_new():
    return render_template('customer_form.html', customer=None)

@app.route('/ui/customers/<int:id>/edit')
def ui_customers_edit(id):
    customer = get_customer_by_id(id)
    return render_template('customer_form.html', customer=customer)

# Suppliers UI
@app.route('/ui/suppliers')
def ui_suppliers_list():
    q = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()
    sort = request.args.get('sort', '').strip()
    page = request.args.get('page', 1, type=int) or 1

    suppliers, total = search_suppliers(q=q, status=status, sort=sort,
                                        page=page, per_page=PER_PAGE)
    pager = _paginate(page, total)
    return render_template('suppliers_list.html', suppliers=suppliers,
                           q=q, status=status, sort=sort, pager=pager)

@app.route('/ui/suppliers/new')
def ui_suppliers_new():
    return render_template('supplier_form.html', supplier=None)

@app.route('/ui/suppliers/<int:id>/edit')
def ui_suppliers_edit(id):
    supplier = get_supplier_by_id(id)
    return render_template('supplier_form.html', supplier=supplier)

# Sales UI
@app.route('/ui/sales')
def ui_sales_list():
    q = request.args.get('q', '').strip()
    sort = request.args.get('sort', '').strip()
    page = request.args.get('page', 1, type=int) or 1

    sales, total = search_sales(q=q, sort=sort, page=page, per_page=PER_PAGE)
    pager = _paginate(page, total)
    return render_template('sales_list.html', sales=sales,
                           q=q, sort=sort, pager=pager)

@app.route('/ui/sales/new')
def ui_sales_new():
    customers = get_all_customers()
    medicines = get_all_medicines()
    return render_template('sale_form.html', sale=None, customers=customers,
                           medicines=medicines, sale_items=[])

@app.route('/ui/sales/<int:id>/edit')
def ui_sales_edit(id):
    sale = get_sale_by_id(id)
    if not sale:
        return redirect('/ui/sales')
    customers = get_all_customers()
    medicines = get_all_medicines()
    return render_template('sale_form.html', sale=sale, customers=customers,
                           medicines=medicines, sale_items=get_sale_items(id))

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG') == '1'
    app.run(debug=debug)