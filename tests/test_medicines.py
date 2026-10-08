import pytest
import sqlite3
import os
import sys

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import init_db, get_db

@pytest.fixture
def client():
    import db
    db.DATABASE_PATH = 'test_pharmacy_medicines.db'
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

def test_get_empty_medicines(client):
    rv = client.get('/api/medicines/')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['status'] == 200
    assert len(json_data['data']) == 0

def test_create_medicine_success(client):
    payload = {
        "medicine_name": "Paracetamol 500mg",
        "selling_price": 2.50,
        "cost_price": 1.20,
        "current_stock": 100
    }
    rv = client.post('/api/medicines/', json=payload)
    assert rv.status_code == 201
    json_data = rv.get_json()
    assert json_data['status'] == 201
    assert json_data['data']['medicine_name'] == "Paracetamol 500mg"

def test_create_medicine_validation_error(client):
    # Missing medicine_name
    payload = {
        "selling_price": 2.50,
        "cost_price": 1.20,
        "current_stock": 100
    }
    rv = client.post('/api/medicines/', json=payload)
    assert rv.status_code == 422
    json_data = rv.get_json()
    assert json_data['status'] == 422
    assert json_data['field'] == 'medicine_name'

def test_create_medicine_boundary_huge_stock(client):
    # Adversarial test: huge number
    payload = {
        "medicine_name": "Too Many Pills",
        "selling_price": 2.50,
        "cost_price": 1.20,
        "current_stock": 9999999999999999999
    }
    rv = client.post('/api/medicines/', json=payload)
    assert rv.status_code == 422
    json_data = rv.get_json()
    assert json_data['field'] == 'current_stock'

def test_create_medicine_xss_input(client):
    # Adversarial test: script tags
    payload = {
        "medicine_name": "<script>alert(1)</script>",
        "selling_price": 2.50,
        "cost_price": 1.20,
        "current_stock": 100
    }
    rv = client.post('/api/medicines/', json=payload)
    assert rv.status_code == 422
    json_data = rv.get_json()
    assert json_data['field'] == 'medicine_name'

def test_update_medicine(client):
    # Create first
    payload = {
        "medicine_name": "Aspirin",
        "selling_price": 3.0,
        "cost_price": 1.5,
        "current_stock": 50
    }
    client.post('/api/medicines/', json=payload)
    
    # Update
    update_payload = {
        "medicine_name": "Aspirin Extra",
        "selling_price": 3.5,
        "cost_price": 1.5,
        "current_stock": 40
    }
    rv = client.put('/api/medicines/1', json=update_payload)
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['data']['medicine_name'] == "Aspirin Extra"
    assert json_data['data']['selling_price'] == 3.5

def test_delete_medicine(client):
    # Create first
    payload = {
        "medicine_name": "Delete Me",
        "selling_price": 1.0,
        "cost_price": 0.5,
        "current_stock": 10
    }
    client.post('/api/medicines/', json=payload)
    
    # Delete (with admin header)
    rv = client.delete('/api/medicines/1', headers={'Authorization': 'Bearer admin-token'})
    assert rv.status_code == 200
    
    # Verify deletion
    rv_get = client.get('/api/medicines/1')
    assert rv_get.status_code == 404
