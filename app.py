"""
app.py — Pharmacy Inventory and Sales Management System
Wire: route -> validation (422) -> thin controller (201/200) -> standardized envelope
Week 4 + Week 5 Deliverable 2 (Routing, Logic & Tests, 25%)
Repo: https://github.com/jmharnaiz/Pharmacy-Inventory-and-Sales-Management-System
Drag-and-drop to repo root. Run: pip install -r requirements.txt && python app.py
"""
import re
from datetime import datetime
from flask import Flask, request, jsonify, session
from functools import wraps
from src.validation import (
    validation_error, success_response, require_roles,
    _is_int, _is_number, EMAIL_RE, PHONE_RE, CODE_RE,
    ALLOWED_CATEGORIES, ALLOWED_STATUSES, ALLOWED_PAYMENT,
    is_valid_date_ymd, is_future_date
)
from src.models.db import init_db, get_db
from src.controllers.medicine_controller import (
    create_medicine_controller, list_medicines_controller, show_medicine_controller,
    update_medicine_controller, delete_medicine_controller
)
from src.controllers.supplier_controller import (
    create_supplier_controller, list_suppliers_controller, show_supplier_controller,
    update_supplier_controller, delete_supplier_controller
)
from src.controllers.customer_controller import (
    create_customer_controller, list_customers_controller, show_customer_controller,
    update_customer_controller, delete_customer_controller
)
from src.controllers.sale_controller import (
    create_sale_controller, list_sales_controller, show_sale_controller,
    update_sale_status_controller
)

app = Flask(__name__)
app.secret_key = "pharmacy_secret_2026"

def login_required(f):
    @wraps(f)
    def w(*a, **kw):
        if "user_id" not in session:
            return jsonify({"status":401,"error":"login required","field":"auth"}),401
        return f(*a, **kw)
    return w

# ---------- Auth ----------
@app.route("/auth/login", methods=["POST"])
def login():
    data=request.get_json(silent=True) or {}
    username=str(data.get("username","")).strip()
    password=str(data.get("password","")).strip()
    if not username: return validation_error("username","username is required")
    if not password: return validation_error("password","password is required")
    conn=get_db(); user=conn.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password)).fetchone(); conn.close()
    if not user: return jsonify({"status":401,"error":"invalid credentials","field":"auth"}),401
    session["user_id"]=user["id"]; session["role"]=user["role"]; session["username"]=user["username"]
    return success_response({"role":user["role"], "username":user["username"]},200)

@app.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return success_response({"ok":True})

@app.route("/auth/change-password", methods=["PUT"])
@login_required
def changePassword():
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required")
    old=str(data.get("old_password","")); new=str(data.get("new_password","")); confirm=str(data.get("confirm_password",""))
    if not old: return validation_error("old_password","old_password is required")
    if not new: return validation_error("new_password","new_password is required")
    if len(new)<8 or len(new)>100: return validation_error("new_password","new_password must be 8-100 chars")
    if not confirm: return validation_error("confirm_password","confirm_password is required")
    if new!=confirm: return validation_error("confirm_password","confirm_password must match new_password")
    return success_response({"changed":True},200)

# ---------- Medicines ----------
@app.route("/medicines", methods=["POST"])
@login_required
def createMedicineRoute():
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required and must be JSON")
    # presence + type + length/range + format + allowed values + referential
    code=str(data.get("medicine_code","")).strip()
    if not code: return validation_error("medicine_code","medicine_code is required")
    if len(code)<1 or len(code)>20: return validation_error("medicine_code","medicine_code must be 1-20 chars")
    if not CODE_RE.match(code): return validation_error("medicine_code","medicine_code format invalid (alphanumeric, -, _)")
    name=str(data.get("medicine_name","")).strip()
    if not name: return validation_error("medicine_name","medicine_name is required")
    if len(name)>100: return validation_error("medicine_name","medicine_name too long (max 100)")
    generic=str(data.get("generic_name","")).strip()
    if generic and len(generic)>100: return validation_error("generic_name","generic_name too long (max 100)")
    category=str(data.get("category","")).strip()
    if not category: return validation_error("category","category is required")
    if category not in ALLOWED_CATEGORIES: return validation_error("category",f"category must be one of {', '.join(sorted(ALLOWED_CATEGORIES))}")
    brand=str(data.get("brand","")).strip()
    if not brand: return validation_error("brand","brand is required")
    if len(brand)>100: return validation_error("brand","brand too long (max 100)")
    supplier_id=data.get("supplier_id")
    if supplier_id is not None and str(supplier_id).strip()!="":
        if not _is_int(supplier_id): return validation_error("supplier_id","supplier_id must be a number")
        conn=get_db()
        if not conn.execute("SELECT id FROM suppliers WHERE id=?",(int(supplier_id),)).fetchone():
            conn.close(); return validation_error("supplier_id","supplier does not exist (referential)")
        conn.close()
        supplier_id=int(supplier_id)
    else:
        supplier_id=None
    unit_price=data.get("unit_price")
    if unit_price is None or str(unit_price).strip()=="": return validation_error("unit_price","unit_price is required")
    if not _is_number(unit_price): return validation_error("unit_price","unit_price must be a number")
    if float(unit_price)<0 or float(unit_price)>999999: return validation_error("unit_price","unit_price out of range (0-999999)")
    qty=data.get("quantity")
    if qty is None or str(qty).strip()=="": return validation_error("quantity","quantity is required")
    if not _is_int(qty): return validation_error("quantity","quantity must be a number")
    if int(qty)<0 or int(qty)>99999: return validation_error("quantity","quantity out of range (0-99999)")
    exp=str(data.get("expiration_date","")).strip()
    if not exp: return validation_error("expiration_date","expiration_date is required")
    if not is_valid_date_ymd(exp): return validation_error("expiration_date","expiration_date must be YYYY-MM-DD format")
    # optionally ensure future date (defensive): allow past but status Expired handling, here we just validate format; future check for non-expired
    status=str(data.get("status","")).strip() or "Available"
    if status not in ALLOWED_STATUSES: return validation_error("status",f"status must be one of {', '.join(sorted(ALLOWED_STATUSES))}")
    conn=get_db()
    if conn.execute("SELECT id FROM medicines WHERE medicine_code=?",(code,)).fetchone():
        conn.close(); return validation_error("medicine_code","medicine_code already exists")
    conn.close()
    validated={"medicine_code":code,"medicine_name":name,"generic_name":generic,"category":category,"brand":brand,"supplier_id":supplier_id,"unit_price":float(unit_price),"quantity":int(qty),"expiration_date":exp,"status":status}
    return create_medicine_controller(validated)

@app.route("/medicines", methods=["GET"])
@login_required
def listMedicinesRoute():
    return list_medicines_controller()

@app.route("/medicines/<int:id>", methods=["GET"])
@login_required
def showMedicineRoute(id):
    conn=get_db()
    if not conn.execute("SELECT id FROM medicines WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","medicine does not exist")
    conn.close()
    return show_medicine_controller(id)

@app.route("/medicines/<int:id>", methods=["PUT"])
@login_required
def updateMedicineRoute(id):
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required")
    conn=get_db()
    if not conn.execute("SELECT id FROM medicines WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","medicine does not exist")
    conn.close()
    code=str(data.get("medicine_code","")).strip()
    if not code: return validation_error("medicine_code","medicine_code is required")
    if len(code)>20: return validation_error("medicine_code","medicine_code must be 1-20 chars")
    if not CODE_RE.match(code): return validation_error("medicine_code","medicine_code format invalid")
    name=str(data.get("medicine_name","")).strip()
    if not name: return validation_error("medicine_name","medicine_name is required")
    if len(name)>100: return validation_error("medicine_name","medicine_name too long")
    category=str(data.get("category","")).strip()
    if not category: return validation_error("category","category is required")
    if category not in ALLOWED_CATEGORIES: return validation_error("category",f"category must be one of {', '.join(sorted(ALLOWED_CATEGORIES))}")
    brand=str(data.get("brand","")).strip()
    if not brand: return validation_error("brand","brand is required")
    supplier_id=data.get("supplier_id")
    if supplier_id is not None and str(supplier_id).strip()!="":
        if not _is_int(supplier_id): return validation_error("supplier_id","supplier_id must be a number")
        conn=get_db()
        if not conn.execute("SELECT id FROM suppliers WHERE id=?",(int(supplier_id),)).fetchone():
            conn.close(); return validation_error("supplier_id","supplier does not exist (referential)")
        conn.close()
        supplier_id=int(supplier_id)
    else:
        supplier_id=None
    unit_price=data.get("unit_price")
    if unit_price is None or str(unit_price).strip()=="": return validation_error("unit_price","unit_price is required")
    if not _is_number(unit_price): return validation_error("unit_price","unit_price must be a number")
    if float(unit_price)<0 or float(unit_price)>999999: return validation_error("unit_price","unit_price out of range (0-999999)")
    qty=data.get("quantity")
    if qty is None or str(qty).strip()=="": return validation_error("quantity","quantity is required")
    if not _is_int(qty): return validation_error("quantity","quantity must be a number")
    if int(qty)<0 or int(qty)>99999: return validation_error("quantity","quantity out of range (0-99999)")
    exp=str(data.get("expiration_date","")).strip()
    if not exp: return validation_error("expiration_date","expiration_date is required")
    if not is_valid_date_ymd(exp): return validation_error("expiration_date","expiration_date must be YYYY-MM-DD format")
    status=str(data.get("status","")).strip() or "Available"
    if status not in ALLOWED_STATUSES: return validation_error("status",f"status must be one of {', '.join(sorted(ALLOWED_STATUSES))}")
    # unique check excluding self
    conn=get_db()
    row=conn.execute("SELECT id FROM medicines WHERE medicine_code=? AND id!=?",(code,id)).fetchone()
    conn.close()
    if row: return validation_error("medicine_code","medicine_code already exists")
    validated={"medicine_code":code,"medicine_name":name,"generic_name":str(data.get("generic_name","")).strip(),"category":category,"brand":brand,"supplier_id":supplier_id,"unit_price":float(unit_price),"quantity":int(qty),"expiration_date":exp,"status":status}
    return update_medicine_controller(id, validated)

@app.route("/medicines/<int:id>", methods=["DELETE"])
@login_required
def deleteMedicineRoute(id):
    auth=require_roles("Admin")
    if auth: return auth
    conn=get_db()
    if not conn.execute("SELECT id FROM medicines WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","medicine does not exist")
    # referential: medicine has sale_items?
    if conn.execute("SELECT id FROM sale_items WHERE medicine_id=? LIMIT 1",(id,)).fetchone():
        conn.close(); return validation_error("id","medicine has sales records (referential)")
    conn.close()
    return delete_medicine_controller(id)

@app.route("/medicines/<int:id>/stock", methods=["PUT"])
@login_required
def updateStockRoute(id):
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required")
    conn=get_db()
    if not conn.execute("SELECT id FROM medicines WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","medicine does not exist")
    conn.close()
    qty=data.get("quantity")
    if qty is None or str(qty).strip()=="": return validation_error("quantity","quantity is required")
    if not _is_int(qty): return validation_error("quantity","quantity must be a number")
    if int(qty)<0 or int(qty)>99999: return validation_error("quantity","quantity out of range (0-99999)")
    # reuse update controller with current record values patched
    from src.models.db import get_medicine
    current=get_medicine(id)
    validated={**current, "quantity": int(qty)}
    # ensure code stays same etc.
    return update_medicine_controller(id, validated)

# ---------- Suppliers ----------
@app.route("/suppliers", methods=["POST"])
@login_required
def createSupplierRoute():
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required")
    company=str(data.get("company_name","")).strip()
    if not company: return validation_error("company_name","company_name is required")
    if len(company)>100: return validation_error("company_name","company_name too long (max 100)")
    contact=str(data.get("contact_person","")).strip()
    if not contact: return validation_error("contact_person","contact_person is required")
    if len(contact)>100: return validation_error("contact_person","contact_person too long (max 100)")
    phone=str(data.get("phone","")).strip()
    if phone:
        if len(phone)>20: return validation_error("phone","phone too long (max 20)")
        if not PHONE_RE.match(phone): return validation_error("phone","phone format invalid")
    email=str(data.get("email","")).strip()
    if email:
        if len(email)>100: return validation_error("email","email too long")
        if not EMAIL_RE.match(email): return validation_error("email","email format invalid")
    address=str(data.get("address",""))
    if len(address)>200: return validation_error("address","address too long (max 200)")
    validated={"company_name":company,"contact_person":contact,"phone":phone,"email":email,"address":address}
    return create_supplier_controller(validated)

@app.route("/suppliers", methods=["GET"])
@login_required
def listSuppliersRoute(): return list_suppliers_controller()

@app.route("/suppliers/<int:id>", methods=["GET"])
@login_required
def showSupplierRoute(id):
    conn=get_db()
    if not conn.execute("SELECT id FROM suppliers WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","supplier does not exist")
    conn.close()
    return show_supplier_controller(id)

@app.route("/suppliers/<int:id>", methods=["PUT"])
@login_required
def updateSupplierRoute(id):
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required")
    conn=get_db()
    if not conn.execute("SELECT id FROM suppliers WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","supplier does not exist")
    conn.close()
    company=str(data.get("company_name","")).strip()
    if not company: return validation_error("company_name","company_name is required")
    if len(company)>100: return validation_error("company_name","company_name too long")
    contact=str(data.get("contact_person","")).strip()
    if not contact: return validation_error("contact_person","contact_person is required")
    email=str(data.get("email","")).strip()
    if email and not EMAIL_RE.match(email): return validation_error("email","email format invalid")
    phone=str(data.get("phone","")).strip()
    if phone and not PHONE_RE.match(phone): return validation_error("phone","phone format invalid")
    validated={"company_name":company,"contact_person":contact,"phone":phone,"email":email,"address":data.get("address","")}
    return update_supplier_controller(id, validated)

@app.route("/suppliers/<int:id>", methods=["DELETE"])
@login_required
def deleteSupplierRoute(id):
    auth=require_roles("Admin")
    if auth: return auth
    conn=get_db()
    if not conn.execute("SELECT id FROM suppliers WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","supplier does not exist")
    if conn.execute("SELECT id FROM medicines WHERE supplier_id=? LIMIT 1",(id,)).fetchone():
        conn.close(); return validation_error("id","supplier has medicines (referential)")
    conn.close()
    return delete_supplier_controller(id)

# ---------- Customers ----------
@app.route("/customers", methods=["POST"])
@login_required
def createCustomerRoute():
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required")
    name=str(data.get("customer_name","")).strip()
    if not name: return validation_error("customer_name","customer_name is required")
    if len(name)>100: return validation_error("customer_name","customer_name too long (max 100)")
    contact=str(data.get("contact_number","")).strip()
    if contact:
        if len(contact)>20: return validation_error("contact_number","contact_number too long")
        if not PHONE_RE.match(contact): return validation_error("contact_number","contact_number format invalid")
    email=str(data.get("email","")).strip()
    if email:
        if len(email)>100: return validation_error("email","email too long")
        if not EMAIL_RE.match(email): return validation_error("email","email format invalid")
    address=str(data.get("address",""))
    if len(address)>200: return validation_error("address","address too long (max 200)")
    validated={"customer_name":name,"contact_number":contact,"email":email,"address":address}
    return create_customer_controller(validated)

@app.route("/customers", methods=["GET"])
@login_required
def listCustomersRoute(): return list_customers_controller()

@app.route("/customers/<int:id>", methods=["GET"])
@login_required
def showCustomerRoute(id):
    conn=get_db()
    if not conn.execute("SELECT id FROM customers WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","customer does not exist")
    conn.close()
    return show_customer_controller(id)

@app.route("/customers/<int:id>", methods=["PUT"])
@login_required
def updateCustomerRoute(id):
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required")
    conn=get_db()
    if not conn.execute("SELECT id FROM customers WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","customer does not exist")
    conn.close()
    name=str(data.get("customer_name","")).strip()
    if not name: return validation_error("customer_name","customer_name is required")
    if len(name)>100: return validation_error("customer_name","customer_name too long")
    contact=str(data.get("contact_number","")).strip()
    if contact and not PHONE_RE.match(contact): return validation_error("contact_number","contact_number format invalid")
    email=str(data.get("email","")).strip()
    if email and not EMAIL_RE.match(email): return validation_error("email","email format invalid")
    validated={"customer_name":name,"contact_number":contact,"email":email,"address":data.get("address","")}
    return update_customer_controller(id, validated)

@app.route("/customers/<int:id>", methods=["DELETE"])
@login_required
def deleteCustomerRoute(id):
    auth=require_roles("Admin")
    if auth: return auth
    conn=get_db()
    if not conn.execute("SELECT id FROM customers WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","customer does not exist")
    if conn.execute("SELECT id FROM sales WHERE customer_id=? LIMIT 1",(id,)).fetchone():
        conn.close(); return validation_error("id","customer has sales records (referential)")
    conn.close()
    return delete_customer_controller(id)

# ---------- Sales ----------
@app.route("/sales", methods=["POST"])
@login_required
def createSaleRoute():
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required and must be JSON")
    # items required, array 1-100, referential each medicine_id exists, qty 1-999, also stock check
    items=data.get("items")
    if items is None: return validation_error("items","items is required")
    if not isinstance(items, list): return validation_error("items","items must be an array")
    if len(items)==0: return validation_error("items","Cart empty: at least one item required")
    if len(items)>100: return validation_error("items","items too many (max 100)")
    validated_items=[]
    for idx, it in enumerate(items):
        if not isinstance(it, dict): return validation_error(f"items[{idx}]","item must be an object")
        mid=it.get("medicine_id")
        if mid is None or str(mid).strip()=="": return validation_error(f"items[{idx}].medicine_id","medicine_id is required")
        if not _is_int(mid): return validation_error(f"items[{idx}].medicine_id","medicine_id must be a number")
        qty=it.get("quantity")
        if qty is None or str(qty).strip()=="": return validation_error(f"items[{idx}].quantity","quantity is required")
        if not _is_int(qty): return validation_error(f"items[{idx}].quantity","quantity must be a number")
        if int(qty)<1 or int(qty)>999: return validation_error(f"items[{idx}].quantity","quantity out of range (1-999)")
        conn=get_db()
        med=conn.execute("SELECT * FROM medicines WHERE id=?",(int(mid),)).fetchone()
        conn.close()
        if not med: return validation_error("items.medicine_id","medicine does not exist (referential)")
        # stock check (referential + range)
        if int(qty) > med["quantity"]: return validation_error(f"items[{idx}].quantity","insufficient stock")
        # expiration check
        try:
            exp_date=datetime.strptime(med["expiration_date"], "%Y-%m-%d").date()
            if exp_date < datetime.now().date():
                return validation_error(f"items[{idx}].medicine_id","medicine is expired")
        except: pass
        validated_items.append({"medicine_id":int(mid),"quantity":int(qty),"unit_price": float(med["unit_price"])})
    customer_id=data.get("customer_id")
    if customer_id is not None and str(customer_id).strip()!="":
        if not _is_int(customer_id): return validation_error("customer_id","customer_id must be a number")
        conn=get_db()
        if not conn.execute("SELECT id FROM customers WHERE id=?",(int(customer_id),)).fetchone():
            conn.close(); return validation_error("customer_id","customer does not exist (referential)")
        conn.close()
        customer_id=int(customer_id)
    else:
        customer_id=None
    payment=str(data.get("payment_method","")).strip()
    if not payment: return validation_error("payment_method","payment_method is required")
    if payment not in ALLOWED_PAYMENT: return validation_error("payment_method",f"payment_method must be one of {', '.join(sorted(ALLOWED_PAYMENT))}")
    status=str(data.get("status","Completed")).strip() or "Completed"
    if status not in {"Completed","Pending","Cancelled","Hold"}: return validation_error("status","status must be one of Completed, Pending, Cancelled, Hold")
    # total_amount: if provided validate, else compute
    total=0
    for it in validated_items:
        total += it["quantity"]*it["unit_price"]
    provided_total=data.get("total_amount")
    if provided_total is not None and str(provided_total).strip()!="":
        if not _is_number(provided_total): return validation_error("total_amount","total_amount must be a number")
        if float(provided_total)<0 or float(provided_total)>9999999: return validation_error("total_amount","total_amount out of range")
        # allow small float diff but require match
        if abs(float(provided_total)-total) > 0.01:
            return validation_error("total_amount","total_amount does not match items total")
        total=float(provided_total)
    transaction_date=str(data.get("transaction_date","")).strip() or datetime.now().strftime("%Y-%m-%d")
    if not is_valid_date_ymd(transaction_date): return validation_error("transaction_date","transaction_date must be YYYY-MM-DD format")
    cashier=str(data.get("cashier","")).strip() or session.get("username","")
    validated={"transaction_date":transaction_date,"customer_id":customer_id,"cashier":cashier,"total_amount":total,"payment_method":payment,"status":status,"items":validated_items}
    return create_sale_controller(validated)

@app.route("/sales", methods=["GET"])
@login_required
def listSalesRoute(): return list_sales_controller()

@app.route("/sales/<int:id>", methods=["GET"])
@login_required
def showSaleRoute(id):
    conn=get_db()
    if not conn.execute("SELECT id FROM sales WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","sale does not exist")
    conn.close()
    return show_sale_controller(id)

@app.route("/sales/<int:id>/status", methods=["PUT"])
@login_required
def updateSaleStatusRoute(id):
    data=request.get_json(silent=True)
    if data is None: return validation_error("body","request body is required")
    conn=get_db()
    if not conn.execute("SELECT id FROM sales WHERE id=?",(id,)).fetchone():
        conn.close(); return validation_error("id","sale does not exist")
    conn.close()
    status=str(data.get("status","")).strip()
    if not status: return validation_error("status","status is required")
    if not isinstance(status, str): return validation_error("status","status must be a string")
    if status not in {"Completed","Pending","Cancelled","Hold"}: return validation_error("status",f"status must be one of Completed, Pending, Cancelled, Hold")
    return update_sale_status_controller(id, {"status": status})

@app.route("/sales/<int:id>/cancel", methods=["POST"])
@login_required
def cancelSaleRoute(id):
    # sensitive: Admin/Cashier only → 403 for Pharmacist
    auth=require_roles("Admin","Cashier")
    if auth: return auth
    conn=get_db()
    row=conn.execute("SELECT * FROM sales WHERE id=?",(id,)).fetchone()
    if not row:
        conn.close(); return validation_error("id","sale does not exist")
    if row["status"]=="Cancelled":
        conn.close(); return validation_error("status","sale already cancelled")
    conn.close()
    return update_sale_status_controller(id, {"status":"Cancelled"})

# ---------- 404/500 ----------
@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith(("/api","/medicines","/suppliers","/customers","/sales","/auth")):
        return jsonify({"status":404,"error":"not found","field":"url"}),404
    return "Not found",404

@app.errorhandler(500)
def handle_500(e):
    return jsonify({"status":500,"error":"internal server error","field":"server"}),500

# also expose alias routes for frontend simplicity
@app.route("/api/sales", methods=["POST"])
@login_required
def apiCreateSaleAlias():
    return createSaleRoute()

@app.route("/")
def index():
    return jsonify({"status":200,"data":{"message":"Pharmacy API running","docs":"/docs/routes.md"}}),200

if __name__=="__main__":
    init_db()
    app.run(debug=True, port=5000)
