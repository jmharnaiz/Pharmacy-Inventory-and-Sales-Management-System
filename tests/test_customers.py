import pytest
import sqlite3
import os
import sys

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import init_db

@pytest.fixture
def client():
    import db
    db.DATABASE_PATH = 'test_pharmacy_customers.db'
    if os.path.exists(db.DATABASE_PATH):
        os.remove(db.DATABASE_PATH)
    init_db()
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
        
    # Cleanup
    if os.path.exists(db.DATABASE_PATH):
        try:
            os.remove(db.DATABASE_PATH)
        except:
            pass

def test_create_customer_success(client):
    payload = {
        "customer_name": "Juan Dela Paz",
        "email": "juan@example.com"
    }
    rv = client.post('/api/customers/', json=payload)
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['status'] == 201
    assert json_data['data']['customer_name'] == "Juan Dela Paz"

def test_create_customer_validation_error(client):
    payload = {
        "email": "invalid@example.com"
    }
    rv = client.post('/api/customers/', json=payload)
    assert rv.status_code == 422
    json_data = rv.get_json()
    assert json_data['status'] == 422
    assert json_data['field'] == "customer_name"

def test_get_customer_not_found(client):
    rv = client.get('/api/customers/999')
    assert rv.status_code == 404
    json_data = rv.get_json()
    assert json_data['status'] == 404
