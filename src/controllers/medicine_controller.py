"""
controllers/medicine_controller.py — Week 5 Task 1: Thin controllers (Pharmacy)
Takes validated data, calls data layer, returns standardized envelope.
No validation here — guard clauses already passed in routes.
"""
from src.models.db import save_medicine, get_medicine, list_medicines, update_medicine, delete_medicine
from src.validation import success_response

def create_medicine_controller(validated):
    nid = save_medicine(
        validated["medicine_code"],
        validated["medicine_name"],
        validated.get("generic_name",""),
        validated["category"],
        validated["brand"],
        validated.get("supplier_id"),
        validated["unit_price"],
        validated["quantity"],
        validated["expiration_date"],
        validated["status"]
    )
    record = get_medicine(nid)
    return success_response(record, 201)

def list_medicines_controller():
    rows = list_medicines()
    return success_response(rows, 200)

def show_medicine_controller(id):
    rec = get_medicine(id)
    return success_response(rec, 200)

def update_medicine_controller(id, validated):
    update_medicine(
        id,
        validated["medicine_code"],
        validated["medicine_name"],
        validated.get("generic_name",""),
        validated["category"],
        validated["brand"],
        validated.get("supplier_id"),
        validated["unit_price"],
        validated["quantity"],
        validated["expiration_date"],
        validated["status"]
    )
    return success_response(get_medicine(id), 200)

def delete_medicine_controller(id):
    delete_medicine(id)
    return success_response({"deleted": id}, 200)
