"""
tests/test_medicines.py — Week 5 Task 3: Arrange-Act-Assert (Pharmacy)
Each controller: 1 happy path, 1 validation failure, 1 edge case
Run: pytest -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app
from src.models.db import init_db

def login(c, user="admin", pw="admin123"):
    c.post("/auth/login", json={"username":user,"password":pw})

def test_createMedicine_saves_valid():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        payload={"medicine_code":"MED-HAPPY-01","medicine_name":"Paracetamol 500mg","generic_name":"Paracetamol","category":"Analgesic","brand":"Biogesic","supplier_id":1,"unit_price":7.50,"quantity":100,"expiration_date":"2027-12-31","status":"Available"}
        resp=c.post("/medicines", json=payload)
        assert resp.status_code==201, resp.get_data(as_text=True)
        data=resp.get_json()
        assert data["status"]==201
        assert "data" in data
        assert data["data"]["medicine_code"]=="MED-HAPPY-01"
        assert data["data"]["medicine_name"]=="Paracetamol 500mg"

def test_createMedicine_rejects_missing_name():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        payload={"medicine_code":"MED-FAIL-01","category":"Analgesic","brand":"Biogesic","unit_price":5,"quantity":10,"expiration_date":"2027-12-31"}
        resp=c.post("/medicines", json=payload)
        assert resp.status_code==422
        j=resp.get_json()
        assert j["status"]==422
        assert j["field"]=="medicine_name"
        assert "is required" in j["error"]

def test_createMedicine_rejects_wrong_type_quantity():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        payload={"medicine_code":"MED-TYPE","medicine_name":"Test","category":"Analgesic","brand":"Biogesic","unit_price":5,"quantity":"cake","expiration_date":"2027-12-31"}
        resp=c.post("/medicines", json=payload)
        assert resp.status_code==422
        assert resp.get_json()["field"]=="quantity"
        assert "must be a number" in resp.get_json()["error"]

def test_createMedicine_out_of_range_quantity():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        payload={"medicine_code":"MED-RANGE","medicine_name":"Test","category":"Vitamin","brand":"Test","unit_price":5,"quantity":100000,"expiration_date":"2027-12-31"}
        resp=c.post("/medicines", json=payload)
        assert resp.status_code==422
        assert resp.get_json()["field"]=="quantity"
        assert "out of range" in resp.get_json()["error"]

def test_createMedicine_rejects_invalid_category():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        payload={"medicine_code":"MED-CAT","medicine_name":"Test","category":"InvalidCat","brand":"Biogesic","unit_price":5,"quantity":10,"expiration_date":"2027-12-31"}
        resp=c.post("/medicines", json=payload)
        assert resp.status_code==422
        assert resp.get_json()["field"]=="category"

def test_createMedicine_edge_duplicate_code():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        payload={"medicine_code":"MED-DUP","medicine_name":"A","category":"Analgesic","brand":"Biogesic","unit_price":5,"quantity":10,"expiration_date":"2027-12-31"}
        r1=c.post("/medicines", json=payload)
        assert r1.status_code==201
        r2=c.post("/medicines", json=payload)
        assert r2.status_code==422
        assert r2.get_json()["field"]=="medicine_code"
        assert "already exists" in r2.get_json()["error"]

def test_createMedicine_referential_supplier_not_exist():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        payload={"medicine_code":"MED-REF","medicine_name":"Test","category":"Analgesic","brand":"Biogesic","supplier_id":99999,"unit_price":5,"quantity":10,"expiration_date":"2027-12-31"}
        resp=c.post("/medicines", json=payload)
        assert resp.status_code==422
        assert resp.get_json()["field"]=="supplier_id"

def test_updateMedicine_edge_nonexistent():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.put("/medicines/99999", json={"medicine_code":"MED-X","medicine_name":"New","category":"Vitamin","brand":"Biogesic","unit_price":5,"quantity":10,"expiration_date":"2027-12-31","status":"Available"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="id"

def test_deleteMedicine_forbidden_for_cashier():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as cashier:
        login(cashier,"cashier","cashier123")
        resp=cashier.delete("/medicines/1")
        assert resp.status_code==403
        j=resp.get_json()
        assert j["status"]==403
        assert j["field"]=="authorization"

def test_deleteMedicine_happy_for_admin():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c,"admin","admin123")
        c.post("/medicines", json={"medicine_code":"MED-DEL","medicine_name":"To Delete","category":"Vitamin","brand":"Brand","unit_price":10,"quantity":5,"expiration_date":"2027-12-31","status":"Available"})
        # find id
        meds=c.get("/medicines").get_json()["data"]
        mid=[m for m in meds if m["medicine_code"]=="MED-DEL"][0]["id"]
        resp=c.delete(f"/medicines/{mid}")
        assert resp.status_code==200
        assert resp.get_json()["data"]["deleted"]==mid

def test_updateStock_validation():
    init_db()
    app.config["TESTING"]=True
    with app.test_client() as c:
        login(c)
        resp=c.put("/medicines/1/stock", json={"quantity":"cake"})
        assert resp.status_code==422
        assert resp.get_json()["field"]=="quantity"
