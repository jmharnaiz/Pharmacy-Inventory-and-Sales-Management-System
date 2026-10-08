import pytest
import os
import sys

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import init_db

TEST_DB = 'test_pharmacy_security.db'


@pytest.fixture
def client():
    import db
    db.DATABASE_PATH = TEST_DB
    if os.path.exists(db.DATABASE_PATH):
        try: os.remove(db.DATABASE_PATH)
        except: pass
    init_db()

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

    app.config['TESTING'] = True
    if os.path.exists(db.DATABASE_PATH):
        try: os.remove(db.DATABASE_PATH)
        except: pass


def make_medicine(client, name='Paracetamol 500mg', stock=100, price=5.0, cost=2.0):
    rv = client.post('/api/medicines/', json={
        "medicine_name": name,
        "selling_price": price,
        "cost_price": cost,
        "current_stock": stock
    })
    assert rv.status_code == 201
    return rv.get_json()['data']['id']


def stock_row(medicine_id):
    import db
    conn = db.get_db()
    row = conn.execute(
        'SELECT current_stock, status FROM medicines WHERE id = ?', (medicine_id,)).fetchone()
    conn.close()
    return dict(row)


def count_rows(table):
    import db
    conn = db.get_db()
    total = conn.execute('SELECT COUNT(*) AS c FROM ' + table).fetchone()['c']
    conn.close()
    return total


def insert_legacy_sale(sale_id_invoice, total=35.0):
    """Insert a sale row directly (no line items) like the old seed did."""
    import db
    conn = db.get_db()
    cur = conn.execute(
        "INSERT INTO sales (invoice_no, date_time, cashier, total_amount, payment_method, status) "
        "VALUES (?, '2026-01-01 10:00:00', 'admin', ?, 'Cash', 'Completed')",
        (sale_id_invoice, total))
    sale_id = cur.lastrowid
    conn.commit()
    conn.close()
    return sale_id


# --- Password hashing & login -------------------------------------------------

def test_users_route_hashes_passwords(client):
    rv = client.post('/ui/users', data={
        "username": "cashier1", "password": "s3cret!", "role": "Cashier"
    })
    assert rv.status_code == 302

    import db
    conn = db.get_db()
    row = conn.execute("SELECT password, role FROM users WHERE username = 'cashier1'").fetchone()
    conn.close()
    assert row['password'] != 's3cret!'
    assert '$' in row['password']  # werkzeug hash marker

    from controllers.security import check_password
    assert check_password(row['password'], 's3cret!')


def test_plaintext_passwords_are_migrated_on_startup(client):
    import db
    conn = db.get_db()
    conn.execute(
        "INSERT INTO users (username, password, role) VALUES ('oldstaff', 'legacy-plain-1', 'Staff')")
    conn.commit()
    conn.close()

    db.ensure_schema()  # startup migration

    conn = db.get_db()
    row = conn.execute("SELECT password FROM users WHERE username = 'oldstaff'").fetchone()
    conn.close()
    assert row['password'] != 'legacy-plain-1'
    assert '$' in row['password']

    from controllers.security import check_password
    assert check_password(row['password'], 'legacy-plain-1')


def test_login_works_with_hashed_password(client):
    rv = client.post('/login', data={"username": "admin", "password": "admin123"})
    assert rv.status_code == 302
    assert rv.headers['Location'].endswith('/')


def test_login_rejects_wrong_password(client):
    rv = client.post('/login', data={"username": "admin", "password": "wrong"})
    assert rv.status_code == 200
    assert b'Invalid credentials' in rv.get_data()


# --- API login + CSRF enforcement ---------------------------------------------

def _fresh_db_without_testing():
    import db
    db.DATABASE_PATH = TEST_DB
    if os.path.exists(db.DATABASE_PATH):
        try: os.remove(db.DATABASE_PATH)
        except: pass
    init_db()
    app.config['TESTING'] = False
    return db


def test_api_requires_login():
    _fresh_db_without_testing()
    try:
        with app.test_client() as c:
            rv = c.get('/api/medicines/')
            assert rv.status_code == 401
            assert rv.get_json()['status'] == 401
    finally:
        app.config['TESTING'] = True
        if os.path.exists(TEST_DB):
            try: os.remove(TEST_DB)
            except: pass


def test_api_posts_require_csrf_token():
    _fresh_db_without_testing()
    try:
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['user'] = 'admin'
                sess['role'] = 'Administrator'
                sess['csrf_token'] = 'tok-123'

            payload = {
                "medicine_name": "CSRF Test",
                "selling_price": 1.0,
                "cost_price": 0.5,
                "current_stock": 5
            }
            # Missing token -> rejected with 400.
            rv = c.post('/api/medicines/', json=payload)
            assert rv.status_code == 400
            assert rv.get_json()['status'] == 400

            # Valid token -> accepted.
            rv = c.post('/api/medicines/', headers={'X-CSRFToken': 'tok-123'}, json=payload)
            assert rv.status_code == 201
    finally:
        app.config['TESTING'] = True
        if os.path.exists(TEST_DB):
            try: os.remove(TEST_DB)
            except: pass


# --- Derived stock status -------------------------------------------------------

def test_stock_status_derived_from_stock_level(client):
    out_id = make_medicine(client, name='Out Med', stock=0)
    low_id = make_medicine(client, name='Low Med', stock=5)
    ok_id = make_medicine(client, name='Ok Med', stock=100)

    assert stock_row(out_id)['status'] == 'Out of Stock'
    assert stock_row(low_id)['status'] == 'Low Stock'
    assert stock_row(ok_id)['status'] == 'In Stock'

    # Raising the stock flips the status, and dropping it flips it back.
    client.put('/api/medicines/%s' % low_id, json={
        "medicine_name": "Low Med", "selling_price": 5.0, "cost_price": 2.0, "current_stock": 200})
    assert stock_row(low_id)['status'] == 'In Stock'

    client.put('/api/medicines/%s' % ok_id, json={
        "medicine_name": "Ok Med", "selling_price": 5.0, "cost_price": 2.0, "current_stock": 3})
    assert stock_row(ok_id)['status'] == 'Low Stock'


def test_purchase_updates_derived_status(client):
    out_id = make_medicine(client, name='Out Med', stock=0)
    assert stock_row(out_id)['status'] == 'Out of Stock'

    client.post('/ui/purchases', data={
        "supplier_id": "", "medicine_id": str(out_id), "quantity": "200"})
    assert stock_row(out_id)['status'] == 'In Stock'


def test_threshold_from_settings_resyncs_status(client):
    med_id = make_medicine(client, name='Threshold Med', stock=50)
    assert stock_row(med_id)['status'] == 'In Stock'  # default threshold is 10

    client.post('/ui/settings', data={
        "store_name": "My Pharmacy Store",
        "currency": u'\u20b1',
        "low_stock_threshold": "100",
        "invoice_prefix": "INV-",
    })
    assert stock_row(med_id)['status'] == 'Low Stock'  # re-synced on save


# --- Settings persistence --------------------------------------------------------

def test_settings_are_persisted_and_applied(client):
    rv = client.post('/ui/settings', data={
        "store_name": "Green Cross Pharmacy",
        "currency": "$",
        "low_stock_threshold": "25",
        "invoice_prefix": "RX-",
    })
    assert rv.status_code == 302

    from controllers.settings import get_setting
    assert get_setting('store_name') == 'Green Cross Pharmacy'
    assert get_setting('currency') == '$'
    assert get_setting('low_stock_threshold') == '25'
    assert get_setting('invoice_prefix') == 'RX-'


def test_settings_validation_rejects_bad_threshold(client):
    rv = client.post('/ui/settings', data={
        "store_name": "S", "currency": u'\u20b1', "low_stock_threshold": "0", "invoice_prefix": "INV-"})
    assert rv.status_code == 302
    assert rv.headers['Location'].endswith('/settings')

    from controllers.settings import get_setting
    assert get_setting('low_stock_threshold') == '10'  # untouched


def test_invoice_prefix_used_for_new_sales(client):
    client.post('/ui/settings', data={
        "store_name": "S", "currency": u'\u20b1', "low_stock_threshold": "10", "invoice_prefix": "RX-"})
    med = make_medicine(client, stock=10, price=5.0)

    rv = client.post('/api/sales/', json={
        "payment_method": "Cash",
        "items": [{"medicine_id": med, "quantity": 2}]
    })
    assert rv.status_code == 201
    assert rv.get_json()['data']['invoice_no'].startswith('RX-')


# --- Legacy backfill ------------------------------------------------------------

def test_backfill_synthesizes_exact_total_without_touching_stock(client):
    med = make_medicine(client, stock=100, price=5.0)
    med2 = make_medicine(client, name='Second', stock=50, price=10.0)
    sale_id = insert_legacy_sale('INV-LEG', total=35.0)

    from backfill_legacy_sales import backfill_legacy_sales
    assert backfill_legacy_sales() == 1

    import db
    conn = db.get_db()
    items = conn.execute(
        'SELECT medicine_id, quantity, unit_price, subtotal FROM sale_items WHERE sale_id = ?',
        (sale_id,)).fetchall()
    sale = conn.execute('SELECT total_amount, legacy FROM sales WHERE id = ?', (sale_id,)).fetchone()
    conn.close()

    assert sale['legacy'] == 1
    assert len(items) >= 1
    assert round(sum(i['subtotal'] for i in items), 2) == 35.0
    assert all(i['medicine_id'] in (med, med2) for i in items)
    # Stock was not touched by the backfill.
    assert stock_row(med)['current_stock'] == 100
    assert stock_row(med2)['current_stock'] == 50

    # Idempotent: a second run finds nothing to do.
    from backfill_legacy_sales import backfill_legacy_sales as again
    assert again() == 0


def test_editing_backfilled_sale_does_not_restock_synthesized_units(client):
    med = make_medicine(client, stock=100, price=5.0)
    sale_id = insert_legacy_sale('INV-LEG2', total=20.0)  # backfills as 4 x 5.00

    from backfill_legacy_sales import backfill_legacy_sales
    backfill_legacy_sales()
    assert stock_row(med)['current_stock'] == 100

    rv = client.put('/api/sales/%s' % sale_id, json={
        "payment_method": "Cash",
        "items": [{"medicine_id": med, "quantity": 2}]
    })
    assert rv.status_code == 200
    # Only the 2 new units leave stock (100 - 2); the synthesized 4 were never returned.
    assert stock_row(med)['current_stock'] == 98

    import db
    conn = db.get_db()
    sale = conn.execute('SELECT legacy FROM sales WHERE id = ?', (sale_id,)).fetchone()
    conn.close()
    assert sale['legacy'] == 0


def test_deleting_backfilled_sale_does_not_restock(client):
    med = make_medicine(client, stock=100, price=5.0)
    sale_id = insert_legacy_sale('INV-LEG3', total=15.0)

    from backfill_legacy_sales import backfill_legacy_sales
    backfill_legacy_sales()
    assert stock_row(med)['current_stock'] == 100

    rv = client.delete('/api/sales/%s' % sale_id)
    assert rv.status_code == 200
    assert stock_row(med)['current_stock'] == 100
    assert count_rows('sales') == 0