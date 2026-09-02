"""
tests/test_suppliers_customers.py — Suppliers & Customers
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app
from src.models.db import init_db

def login(c, user="admin", pw="admin123"):
    c.post("/auth/login", json={"username":user,"password":pw})

def test_createSupplier_saves_valid():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        payload={"company_name":"New Pharma Co.","contact_person":"John Doe","phone":"09171234567","email":"new@test.com","address":"Manila"}
        resp=c.post("/suppliers", json=payload)
        assert resp.status_code==201
        j=resp.get_json()
        assert j["status"]==201
        assert j["data"]["company_name"]=="New Pharma Co."

def test_createSupplier_rejects_missing_company():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/suppliers", json={"contact_person":"John"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="company_name"

def test_createSupplier_rejects_invalid_email():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/suppliers", json={"company_name":"A","contact_person":"B","email":"not-an-email"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="email"
        assert "format invalid" in resp.get_json()["error"]

def test_createSupplier_edge_invalid_phone():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/suppliers", json={"company_name":"A","contact_person":"B","phone":"abc!!!"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="phone"

def test_deleteSupplier_forbidden_for_cashier():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c,"cashier","cashier123")
        resp=c.delete("/suppliers/1")
        assert resp.status_code==403
        assert resp.get_json()["field"]=="authorization"

def test_deleteSupplier_referential_block():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c,"admin","admin123")
        # supplier 1 has medicines (seed data)
        resp=c.delete("/suppliers/1")
        assert resp.status_code==422
        assert resp.get_json()["field"]=="id"
        assert "referential" in resp.get_json()["error"]

# ----- Customers -----
def test_createCustomer_saves_valid():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        payload={"customer_name":"Maria Clara","contact_number":"09170001234","email":"maria@test.com","address":"Quezon City"}
        resp=c.post("/customers", json=payload)
        assert resp.status_code==201
        assert resp.get_json()["data"]["customer_name"]=="Maria Clara"

def test_createCustomer_rejects_missing_name():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/customers", json={"email":"a@test.com"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="customer_name"

def test_createCustomer_wrong_email_format():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/customers", json={"customer_name":"Test","email":"not-an-email"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="email"

def test_updateCustomer_edge_nonexistent():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.put("/customers/99999", json={"customer_name":"New"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="id"

def test_deleteCustomer_forbidden_for_pharmacist():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c,"pharmacist","pharma123")
        resp=c.delete("/customers/1")
        assert resp.status_code==403
        assert resp.get_json()["field"]=="authorization"
