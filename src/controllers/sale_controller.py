"""
controllers/sale_controller.py — Thin controller for Sales (Week 5)
"""
from src.models.db import save_sale, get_sale, list_sales, update_sale_status
from src.validation import success_response

def create_sale_controller(validated):
    nid = save_sale(
        validated["transaction_date"],
        validated.get("customer_id"),
        validated.get("cashier",""),
        validated["total_amount"],
        validated["payment_method"],
        validated.get("status","Completed"),
        validated["items"]
    )
    record = get_sale(nid)
    return success_response(record, 201)

def list_sales_controller():
    return success_response(list_sales(), 200)

def show_sale_controller(id):
    return success_response(get_sale(id), 200)

def update_sale_status_controller(id, validated):
    update_sale_status(id, validated["status"])
    return success_response(get_sale(id), 200)
