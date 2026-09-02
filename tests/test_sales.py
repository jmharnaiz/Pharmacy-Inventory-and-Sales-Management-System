"""
tests/test_sales.py — Sales (orders) — happy path, validation, edge, auth
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app
from src.models.db import init_db

def login(c, user="admin", pw="admin123"):
    c.post("/auth/login", json={"username":user,"password":pw})

def test_createSale_saves_valid():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        # sale with 1 item, medicine 1 has stock 100, price 5.50
        payload={"items":[{"medicine_id":1,"quantity":2}],"payment_method":"Cash","customer_id":1}
        resp=c.post("/sales", json=payload)
        assert resp.status_code==201, resp.get_data(as_text=True)
        j=resp.get_json()
        assert j["status"]==201
        assert "data" in j
        assert j["data"]["total_amount"]==11.0  # 2 * 5.5
        assert len(j["data"]["items"])==1

def test_createSale_rejects_missing_items():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/sales", json={"payment_method":"Cash"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="items"

def test_createSale_rejects_wrong_type_qty_cake():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/sales", json={"items":[{"medicine_id":1,"quantity":"cake"}],"payment_method":"Cash"})
        assert resp.status_code==422
        assert "quantity" in resp.get_json()["field"]
        assert "must be a number" in resp.get_json()["error"]

def test_createSale_out_of_range_qty():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/sales", json={"items":[{"medicine_id":1,"quantity":0}],"payment_method":"Cash"})
        assert resp.status_code==422
        assert "out of range" in resp.get_json()["error"]
        resp2=c.post("/sales", json={"items":[{"medicine_id":1,"quantity":1000}],"payment_method":"Cash"})
        assert resp2.status_code==422

def test_createSale_referential_invalid_medicine():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/sales", json={"items":[{"medicine_id":99999,"quantity":1}],"payment_method":"Cash"})
        assert resp.status_code==422
        assert "referential" in resp.get_json()["error"]

def test_createSale_rejects_invalid_payment():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/sales", json={"items":[{"medicine_id":1,"quantity":1}],"payment_method":"Bitcoin"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="payment_method"

def test_createSale_edge_insufficient_stock():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        # medicine 1 stock 100, try 999 (exists but more than stock -> could also be range ok but stock fail at 999 > 100)
        # Use 200 > stock 100 but within 1-999
        resp=c.post("/sales", json={"items":[{"medicine_id":1,"quantity":200}],"payment_method":"Cash"})
        assert resp.status_code==422
        assert "insufficient stock" in resp.get_json()["error"]

def test_createSale_edge_empty_cart():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.post("/sales", json={"items":[],"payment_method":"Cash"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="items"

def test_cancelSale_forbidden_for_pharmacist():
    init_db(); app.config["TESTING"]=True
    # create sale as admin
    with app.test_client() as admin:
        login(admin,"admin","admin123")
        admin.post("/sales", json={"items":[{"medicine_id":1,"quantity":1}],"payment_method":"Cash"})
    with app.test_client() as pharma:
        login(pharma,"pharmacist","pharma123")
        resp=pharma.post("/sales/1/cancel")
        assert resp.status_code==403
        assert resp.get_json()["field"]=="authorization"

def test_cancelSale_happy_for_admin():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c,"admin","admin123")
        c.post("/sales", json={"items":[{"medicine_id":1,"quantity":1}],"payment_method":"Cash"})
        resp=c.post("/sales/1/cancel")
        assert resp.status_code==200
        assert resp.get_json()["data"]["status"]=="Cancelled"

def test_updateSaleStatus_validation():
    init_db(); app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        c.post("/sales", json={"items":[{"medicine_id":1,"quantity":1}],"payment_method":"Cash"})
        resp=c.put("/sales/1/status", json={"status":"shipped"})  # invalid
        assert resp.status_code==422
        assert resp.get_json()["field"]=="status"
        resp2=c.put("/sales/1/status", json={"status":""})  # missing
        assert resp2.status_code==422
        resp3=c.put("/sales/1/status", json={"status":"Pending"}) # valid
        assert resp3.status_code==200
