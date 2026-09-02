"""
controllers/supplier_controller.py — Thin controller
"""
from src.models.db import save_supplier, get_supplier, list_suppliers, update_supplier, delete_supplier
from src.validation import success_response

def create_supplier_controller(validated):
    nid = save_supplier(validated["company_name"], validated["contact_person"], validated.get("phone",""), validated.get("email",""), validated.get("address",""))
    return success_response(get_supplier(nid), 201)

def list_suppliers_controller():
    return success_response(list_suppliers(), 200)

def show_supplier_controller(id):
    return success_response(get_supplier(id), 200)

def update_supplier_controller(id, validated):
    update_supplier(id, validated["company_name"], validated["contact_person"], validated.get("phone",""), validated.get("email",""), validated.get("address",""))
    return success_response(get_supplier(id), 200)

def delete_supplier_controller(id):
    delete_supplier(id)
    return success_response({"deleted": id}, 200)
