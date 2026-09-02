"""
validation.py — Week 4 guards + Week 5 success envelope (Pharmacy)
Error:   { "status": 422, "error": "...", "field": "..." }
Success: { "status": 201, "data": { ... } }  /  { "status": 200, "data": [...] }
Auth:    { "status": 403, "error": "...", "field": "authorization" }
"""
import re
from flask import jsonify, session

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+\-\s()]+$")
CODE_RE = re.compile(r"^[A-Za-z0-9\-_]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_CATEGORIES = {"Antibiotic","Analgesic","Vitamin","Antiseptic","Antacid","Antihistamine","Supplement","Syrup","Capsule","Tablet"}
ALLOWED_STATUSES = {"Available","Low Stock","Out of Stock","Expired"}
ALLOWED_PAYMENT = {"Cash","Card","GCash","Bank Transfer"}
ALLOWED_CUSTOMER_FIELDS = {"Walk-in","Regular","Member"}

def validation_error(field, message, status=422):
    return jsonify({"status": status, "error": message, "field": field}), status

def success_response(data, status=200):
    return jsonify({"status": status, "data": data}), status

def require_roles(*allowed):
    role = session.get("role")
    if role not in allowed:
        return jsonify({"status":403,"error":f"not allowed: requires {'/'.join(allowed)} (your role: {role})","field":"authorization"}),403
    return None

def _is_int(v):
    try: int(v); return True
    except: return False

def _is_number(v):
    try: float(v); return True
    except: return False

def is_valid_date_ymd(v):
    if not DATE_RE.match(str(v)): return False
    try:
        from datetime import datetime
        datetime.strptime(v, "%Y-%m-%d"); return True
    except: return False

def is_future_date(v):
    try:
        from datetime import datetime
        d = datetime.strptime(v, "%Y-%m-%d")
        return d.date() >= datetime.now().date()
    except: return False
