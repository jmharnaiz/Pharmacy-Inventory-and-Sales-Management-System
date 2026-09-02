"""
controllers/customer_controller.py — Thin controller
"""
from src.models.db import save_customer, get_customer, list_customers, update_customer, delete_customer
from src.validation import success_response

def create_customer_controller(validated):
    nid = save_customer(validated["customer_name"], validated.get("contact_number",""), validated.get("email",""), validated.get("address",""))
    return success_response(get_customer(nid), 201)

def list_customers_controller():
    return success_response(list_customers(), 200)

def show_customer_controller(id):
    return success_response(get_customer(id), 200)

def update_customer_controller(id, validated):
    update_customer(id, validated["customer_name"], validated.get("contact_number",""), validated.get("email",""), validated.get("address",""))
    return success_response(get_customer(id), 200)

def delete_customer_controller(id):
    delete_customer(id)
    return success_response({"deleted": id}, 200)
