"""Turso-mode tests: the app's durable-backend path.

The real `turso_serverless` driver talks SQL-over-HTTP to Turso Cloud and has
no local mode, so these tests stand in for it with a fake module that exposes
the same surface our code relies on — `connect(url, auth_token)`,
`row_factory = Row` with `row['name']`/`row[0]` access, and the DB-API
exception taxonomy — backed by a real sqlite3 file. That exercises the exact
code path `db.py` uses in Turso mode (schema bootstrap, triggers, lastrowid,
executemany, integrity errors) without network access.
"""

import os
import sys
import sqlite3
import types

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import db


def _make_turso_driver(backend_path):
    driver = types.ModuleType('turso_serverless')

    class Row(object):
        """sqlite3.Row-like: supports row['name'] and row[index]."""

        def __init__(self, cursor, data):
            self._data = tuple(data)
            desc = list(cursor.description) if cursor.description else []
            self._keys = tuple(d[0] for d in desc)
            self._index = {name: i for i, name in enumerate(self._keys)}

        def keys(self):
            return list(self._keys)

        def __getitem__(self, key):
            if isinstance(key, (int, slice)):
                return self._data[key]
            return self._data[self._index[key]]

        def __iter__(self):
            return iter(self._data)

        def __len__(self):
            return len(self._data)

    class Error(Exception):
        pass

    class IntegrityError(Error):
        pass

    class OperationalError(Error):
        pass

    class ProgrammingError(Error):
        pass

    def connect(url, auth_token=None, **kwargs):
        assert url == 'libsql://fake-turso.turso.io'
        assert auth_token == 'fake-token'
        driver.connect_calls += 1
        conn = sqlite3.connect(backend_path)
        conn.row_factory = Row
        return conn

    driver.connect_calls = 0

    driver.Row = Row
    driver.Error = Error
    driver.IntegrityError = IntegrityError
    driver.OperationalError = OperationalError
    driver.ProgrammingError = ProgrammingError
    driver.connect = connect
    return driver


@pytest.fixture
def turso_mode(tmp_path, monkeypatch):
    backend = tmp_path / 'turso_backend.db'
    driver = _make_turso_driver(str(backend))
    monkeypatch.setitem(sys.modules, 'turso_serverless', driver)
    monkeypatch.setattr(db, 'TURSO_URL', 'libsql://fake-turso.turso.io')
    monkeypatch.setattr(db, 'TURSO_AUTH_TOKEN', 'fake-token')
    monkeypatch.setattr(db, 'USING_TURSO', True)
    return backend


# --- get_db plumbing ---------------------------------------------------------

def test_get_db_connects_to_turso_in_turso_mode(turso_mode):
    driver = sys.modules['turso_serverless']
    conn = db.get_db()
    assert driver.connect_calls == 1
    conn.execute('CREATE TABLE probe (id INTEGER PRIMARY KEY, name TEXT)')
    conn.execute("INSERT INTO probe (name) VALUES ('alice')")
    cur = conn.execute("INSERT INTO probe (name) VALUES ('bob')")
    last_id = cur.lastrowid
    conn.commit()
    conn.close()

    # A brand-new connection (fresh cold start) still sees the write.
    conn2 = db.get_db()
    row = conn2.execute('SELECT * FROM probe WHERE id = ?', (last_id,)).fetchone()
    total = conn2.execute('SELECT COUNT(*) AS c FROM probe').fetchone()['c']
    conn2.close()
    assert row['name'] == 'bob'   # name access
    assert row[1] == 'bob'        # index access
    assert total == 2


def test_integrity_errors_tuple_matches_backend(turso_mode):
    types_tuple = db.integrity_errors()
    fake = sys.modules['turso_serverless']
    assert types_tuple == (sqlite3.IntegrityError, fake.IntegrityError)


def test_integrity_errors_local_only(monkeypatch):
    monkeypatch.setattr(db, 'USING_TURSO', False)
    assert db.integrity_errors() == (sqlite3.IntegrityError,)


# --- bootstrap & first boot --------------------------------------------------

def test_fresh_db_bootstraps_schema_and_demo_data(turso_mode):
    db.ensure_schema()

    conn = db.get_db()
    counts = {t: conn.execute('SELECT COUNT(*) AS c FROM ' + t).fetchone()['c']
              for t in ('users', 'medicines', 'customers', 'suppliers',
                        'sales', 'sale_items', 'purchases', 'adjustments')}
    tables = sorted(r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall())
    conn.close()

    assert counts['users'] == 11            # admin + 10 staff
    assert counts['medicines'] == 10
    assert counts['customers'] == 10
    assert counts['suppliers'] == 10
    assert counts['sales'] == 10
    assert counts['sale_items'] >= 10
    assert counts['purchases'] == 10
    assert counts['adjustments'] == 10
    assert set(tables) >= {'medicines', 'sales', 'users', 'settings'}

    # Every demo sale has line items (no legacy orphans on a fresh DB).
    conn = db.get_db()
    no_items = conn.execute(
        'SELECT COUNT(*) AS c FROM sales s WHERE NOT EXISTS '
        '(SELECT 1 FROM sale_items i WHERE i.sale_id = s.id)').fetchone()['c']
    conn.close()
    assert no_items == 0


def test_bootstrap_is_idempotent(turso_mode):
    db.ensure_schema()
    db.ensure_schema()   # app re-runs this on every cold start

    conn = db.get_db()
    users = conn.execute('SELECT COUNT(*) AS c FROM users').fetchone()['c']
    sales = conn.execute('SELECT COUNT(*) AS c FROM sales').fetchone()['c']
    conn.close()
    assert users == 11
    assert sales == 10


def test_admin_login_credentials_seeded_hashed(turso_mode):
    db.ensure_schema()

    from controllers.security import check_password

    conn = db.get_db()
    row = conn.execute("SELECT password, role FROM users WHERE username = 'admin'").fetchone()
    conn.close()
    assert row['role'] == 'Administrator'
    assert '$' in row['password']               # hashed, not plaintext
    assert check_password(row['password'], 'admin123')


# --- persistence across "cold starts" ----------------------------------------

def test_edits_survive_new_connections(turso_mode):
    db.ensure_schema()

    conn = db.get_db()
    conn.execute("UPDATE medicines SET selling_price = 99.50, current_stock = 3 "
                 "WHERE medicine_name = 'Paracetamol 500mg'")
    conn.commit()
    conn.close()

    conn = db.get_db()          # new connection == new cold start
    row = conn.execute(
        "SELECT selling_price, current_stock, status FROM medicines "
        "WHERE medicine_name = 'Paracetamol 500mg'").fetchone()
    conn.close()
    assert row['selling_price'] == 99.5
    assert row['current_stock'] == 3
    assert row['status'] == 'Low Stock'          # derived by trigger (3 <= 10)


def test_settings_persist_across_connections(turso_mode):
    from controllers.settings import save_settings, get_setting

    db.ensure_schema()
    save_settings({'store_name': 'Turso Pharmacy', 'currency': '$',
                   'low_stock_threshold': '5', 'invoice_prefix': 'TINV-'})

    assert get_setting('store_name', '') == 'Turso Pharmacy'
    assert get_setting('currency', '') == '$'
    assert get_setting('low_stock_threshold', '') == '5'
    assert get_setting('invoice_prefix', '') == 'TINV-'


# --- sales flow through the same SQL the app uses ----------------------------

def test_create_sale_uses_lastrowid_and_decrements_stock(turso_mode):
    from controllers.sales import create_sale

    db.ensure_schema()

    conn = db.get_db()
    med = conn.execute('SELECT id, current_stock FROM medicines ORDER BY id LIMIT 1').fetchone()
    conn.close()
    stock_before = med['current_stock']

    sale = create_sale({
        'invoice_no': 'INV-T-1',
        'date_time': '2026-01-01 10:00:00',
        'customer_id': 1,
        'cashier': 'admin',
        'payment_method': 'Cash',
        'items': [{'medicine_id': med['id'], 'quantity': 2, 'unit_price': 5.0}],
    })

    assert sale['id']  # dict(row) works in Turso mode
    assert sale['total_amount'] == 10.0

    conn = db.get_db()
    items = conn.execute('SELECT quantity, subtotal FROM sale_items WHERE sale_id = ?',
                         (sale['id'],)).fetchall()
    stock_after = conn.execute('SELECT current_stock FROM medicines WHERE id = ?',
                               (med['id'],)).fetchone()['current_stock']
    conn.close()
    assert len(items) == 1
    assert items[0]['quantity'] == 2
    assert items[0]['subtotal'] == 10.0
    assert stock_after == stock_before - 2


def test_duplicate_invoice_returns_422_not_500_in_turso_mode(turso_mode):
    from app import app

    app.config['TESTING'] = True
    db.ensure_schema()

    conn = db.get_db()
    med = conn.execute('SELECT id FROM medicines ORDER BY id LIMIT 1').fetchone()
    conn.close()

    client = app.test_client()
    payload = {
        'invoice_no': 'DUP-9', 'customer_id': 1, 'payment_method': 'Cash',
        'date_time': '2026-01-01 10:00:00',
        'items': [{'medicine_id': med['id'], 'quantity': 1, 'unit_price': 5.0}],
    }

    rv1 = client.post('/api/sales/', json=payload)
    assert rv1.status_code == 201

    rv2 = client.post('/api/sales/', json=payload)
    assert rv2.status_code == 422
    assert 'invoice' in rv2.get_json()['error']