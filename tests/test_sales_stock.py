import pytest
import os
import sys

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import init_db

TEST_DB = 'test_pharmacy_sales.db'


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


def stock_of(medicine_id):
    import db
    conn = db.get_db()
    row = conn.execute('SELECT current_stock FROM medicines WHERE id = ?', (medicine_id,)).fetchone()
    conn.close()
    return row['current_stock']


def count_rows(table):
    import db
    conn = db.get_db()
    total = conn.execute('SELECT COUNT(*) AS c FROM ' + table).fetchone()['c']
    conn.close()
    return total


# --- Sales create -----------------------------------------------------------

def test_sale_with_items_decrements_stock(client):
    med = make_medicine(client, stock=100, price=5.0)

    rv = client.post('/api/sales/', json={
        "payment_method": "Cash",
        "items": [{"medicine_id": med, "quantity": 4}]
    })

    assert rv.status_code == 201
    assert stock_of(med) == 96
    # Total is computed server-side from the line items.
    assert rv.get_json()['data']['total_amount'] == 20.0


def test_sale_rejects_missing_line_items(client):
    med = make_medicine(client, stock=10)

    rv = client.post('/api/sales/', json={"payment_method": "Cash", "total_amount": 50})

    assert rv.status_code == 422
    assert rv.get_json()['field'] == 'items'
    assert count_rows('sales') == 0
    assert stock_of(med) == 10


def test_sale_rejects_invalid_quantity(client):
    med = make_medicine(client, stock=10)

    rv = client.post('/api/sales/', json={
        "payment_method": "Cash",
        "items": [{"medicine_id": med, "quantity": 0}]
    })

    assert rv.status_code == 422
    assert rv.get_json()['field'] == 'items'
    assert stock_of(med) == 10


def test_insufficient_stock_rolls_back_the_whole_sale(client):
    plentiful = make_medicine(client, name='Ibuprofen', stock=50, price=2.0)
    scarce = make_medicine(client, name='Rare Drug', stock=2, price=100.0)

    rv = client.post('/api/sales/', json={
        "payment_method": "Cash",
        "items": [
            {"medicine_id": plentiful, "quantity": 5},
            {"medicine_id": scarce, "quantity": 10}
        ]
    })

    assert rv.status_code == 422
    assert 'insufficient stock' in rv.get_json()['error']
    # Nothing was written, including the first line.
    assert count_rows('sales') == 0
    assert count_rows('sale_items') == 0
    assert stock_of(plentiful) == 50
    assert stock_of(scarce) == 2


def test_sale_to_unknown_medicine_fails(client):
    rv = client.post('/api/sales/', json={
        "payment_method": "Cash",
        "items": [{"medicine_id": 9999, "quantity": 1}]
    })

    assert rv.status_code == 422
    assert rv.get_json()['field'] == 'items'
    assert count_rows('sales') == 0


# --- Sales update / delete --------------------------------------------------

def test_update_sale_replaces_lines_and_stock(client):
    med = make_medicine(client, stock=100, price=5.0)

    created = client.post('/api/sales/', json={
        "payment_method": "Cash",
        "items": [{"medicine_id": med, "quantity": 4}]
    }).get_json()['data']
    assert stock_of(med) == 96

    rv = client.put('/api/sales/%s' % created['id'], json={
        "payment_method": "Card",
        "items": [{"medicine_id": med, "quantity": 10}]
    })

    assert rv.status_code == 200
    assert stock_of(med) == 90
    assert rv.get_json()['data']['total_amount'] == 50.0
    assert count_rows('sale_items') == 1


def test_update_sale_with_more_stock_than_available_rolls_back(client):
    med = make_medicine(client, stock=100, price=5.0)

    created = client.post('/api/sales/', json={
        "payment_method": "Cash",
        "items": [{"medicine_id": med, "quantity": 4}]
    }).get_json()['data']

    rv = client.put('/api/sales/%s' % created['id'], json={
        "payment_method": "Cash",
        "items": [{"medicine_id": med, "quantity": 500}]
    })

    assert rv.status_code == 422
    # The original sale and its stock movement survived the failed edit.
    assert stock_of(med) == 96
    assert count_rows('sale_items') == 1


def test_delete_sale_restores_stock(client):
    med = make_medicine(client, stock=100, price=5.0)

    created = client.post('/api/sales/', json={
        "payment_method": "Cash",
        "items": [{"medicine_id": med, "quantity": 4}]
    }).get_json()['data']
    assert stock_of(med) == 96

    rv = client.delete('/api/sales/%s' % created['id'])

    assert rv.status_code == 200
    assert stock_of(med) == 100
    assert count_rows('sale_items') == 0


# --- Purchases (receiving stock) -------------------------------------------

def test_purchase_adds_stock(client):
    med = make_medicine(client, stock=100, cost=2.0)

    rv = client.post('/ui/purchases', data={
        "supplier_id": "",
        "medicine_id": str(med),
        "quantity": "40"
    })

    assert rv.status_code == 302
    assert stock_of(med) == 140
    assert count_rows('purchase_items') == 1


def test_purchase_total_is_computed_from_cost_price(client):
    med = make_medicine(client, stock=100, cost=2.5)

    client.post('/ui/purchases', data={
        "supplier_id": "",
        "medicine_id": str(med),
        "quantity": "10"
    })

    import db
    conn = db.get_db()
    purchase = conn.execute('SELECT * FROM purchases ORDER BY id DESC LIMIT 1').fetchone()
    item = conn.execute('SELECT * FROM purchase_items ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()

    assert purchase['total_amount'] == 25.0
    assert item['unit_cost'] == 2.5
    assert item['subtotal'] == 25.0


def test_purchase_rejects_non_numeric_quantity(client):
    med = make_medicine(client, stock=100)

    rv = client.post('/ui/purchases', data={
        "supplier_id": "",
        "medicine_id": str(med),
        "quantity": "lots"
    })

    assert rv.status_code == 200
    assert 'Quantity must be a whole number' in rv.get_data(as_text=True)
    assert count_rows('purchases') == 0
    assert stock_of(med) == 100


def test_purchase_rejects_unknown_medicine(client):
    rv = client.post('/ui/purchases', data={
        "supplier_id": "",
        "medicine_id": "9999",
        "quantity": "10"
    })

    assert rv.status_code == 200
    assert count_rows('purchases') == 0
