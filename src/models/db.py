"""
models/db.py — Data layer (thin). Only raw persistence, no validation.
Used by thin controllers (Week 5 Task 1).
"""
import os, sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "pharmacy.db")
if not os.path.exists(os.path.dirname(os.path.abspath(DB_PATH))):
    DB_PATH = os.path.join(os.path.dirname(__file__), "pharmacy.db")
DB_PATH = os.path.abspath(DB_PATH)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        contact_person TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT
    );
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_code TEXT UNIQUE NOT NULL,
        medicine_name TEXT NOT NULL,
        generic_name TEXT,
        category TEXT NOT NULL,
        brand TEXT NOT NULL,
        supplier_id INTEGER,
        unit_price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        expiration_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        contact_number TEXT,
        email TEXT,
        address TEXT
    );
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_date TEXT NOT NULL,
        customer_id INTEGER,
        cashier TEXT,
        total_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Completed',
        FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        medicine_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
        FOREIGN KEY(medicine_id) REFERENCES medicines(id)
    );
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    );
    """)
    conn.commit()
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]==0:
        conn.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", ("admin","admin123","Admin"))
        conn.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", ("pharmacist","pharma123","Pharmacist"))
        conn.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", ("cashier","cashier123","Cashier"))
        conn.commit()
    # seed demo suppliers if empty
    if conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]==0:
        conn.execute("INSERT INTO suppliers (company_name,contact_person,phone,email,address) VALUES (?,?,?,?,?)", ("MediSupply Co.","Juan Dela Cruz","09171234567","medisupply@test.com","Manila"))
        conn.execute("INSERT INTO suppliers (company_name,contact_person,phone,email,address) VALUES (?,?,?,?,?)", ("PharmaPlus Inc.","Maria Santos","09179876543","pharmaplus@test.com","Cebu"))
        conn.commit()
    # seed medicines if empty
    if conn.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]==0:
        conn.execute("INSERT INTO medicines (medicine_code,medicine_name,generic_name,category,brand,supplier_id,unit_price,quantity,expiration_date,status) VALUES (?,?,?,?,?,?,?,?,?,?)", ("MED-001","Biogesic","Paracetamol","Analgesic","Biogesic",1,5.50,100,"2027-12-31","Available"))
        conn.execute("INSERT INTO medicines (medicine_code,medicine_name,generic_name,category,brand,supplier_id,unit_price,quantity,expiration_date,status) VALUES (?,?,?,?,?,?,?,?,?,?)", ("MED-002","Amoxicillin 500mg","Amoxicillin","Antibiotic","RiteMed",1,12.00,50,"2027-06-15","Available"))
        conn.execute("INSERT INTO medicines (medicine_code,medicine_name,generic_name,category,brand,supplier_id,unit_price,quantity,expiration_date,status) VALUES (?,?,?,?,?,?,?,?,?,?)", ("MED-003","Ceelin Vitamin C","Ascorbic Acid","Vitamin","Unilab",2,8.00,200,"2027-09-30","Available"))
        conn.commit()
    if conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]==0:
        conn.execute("INSERT INTO customers (customer_name,contact_number,email,address) VALUES (?,?,?,?)", ("Walk-in Customer","09170000001","walkin@test.com",""))
        conn.commit()
    conn.close()

# ----- medicines -----
def save_medicine(code,name,generic,category,brand,supplier_id,unit_price,quantity,exp_date,status):
    conn=get_db()
    cur=conn.execute("INSERT INTO medicines (medicine_code,medicine_name,generic_name,category,brand,supplier_id,unit_price,quantity,expiration_date,status) VALUES (?,?,?,?,?,?,?,?,?,?)",(code,name,generic,category,brand,supplier_id,unit_price,quantity,exp_date,status))
    conn.commit(); nid=cur.lastrowid; conn.close(); return nid

def get_medicine(id):
    conn=get_db(); r=conn.execute("SELECT * FROM medicines WHERE id=?",(id,)).fetchone(); conn.close(); return dict(r) if r else None

def list_medicines():
    conn=get_db(); rows=conn.execute("SELECT * FROM medicines ORDER BY id DESC").fetchall(); conn.close(); return [dict(r) for r in rows]

def update_medicine(id, code,name,generic,category,brand,supplier_id,unit_price,quantity,exp_date,status):
    conn=get_db(); conn.execute("UPDATE medicines SET medicine_code=?,medicine_name=?,generic_name=?,category=?,brand=?,supplier_id=?,unit_price=?,quantity=?,expiration_date=?,status=? WHERE id=?",(code,name,generic,category,brand,supplier_id,unit_price,quantity,exp_date,status,id)); conn.commit(); conn.close()

def delete_medicine(id):
    conn=get_db(); conn.execute("DELETE FROM medicines WHERE id=?",(id,)); conn.commit(); conn.close()

def search_medicines_low_stock(threshold=10):
    conn=get_db(); rows=conn.execute("SELECT * FROM medicines WHERE quantity <= ? ORDER BY quantity ASC",(threshold,)).fetchall(); conn.close(); return [dict(r) for r in rows]

# ----- suppliers -----
def save_supplier(company,contact,phone,email,address):
    conn=get_db(); cur=conn.execute("INSERT INTO suppliers (company_name,contact_person,phone,email,address) VALUES (?,?,?,?,?)",(company,contact,phone,email,address)); conn.commit(); nid=cur.lastrowid; conn.close(); return nid

def get_supplier(id):
    conn=get_db(); r=conn.execute("SELECT * FROM suppliers WHERE id=?",(id,)).fetchone(); conn.close(); return dict(r) if r else None

def list_suppliers():
    conn=get_db(); rows=conn.execute("SELECT * FROM suppliers ORDER BY id DESC").fetchall(); conn.close(); return [dict(r) for r in rows]

def update_supplier(id, company,contact,phone,email,address):
    conn=get_db(); conn.execute("UPDATE suppliers SET company_name=?,contact_person=?,phone=?,email=?,address=? WHERE id=?",(company,contact,phone,email,address,id)); conn.commit(); conn.close()

def delete_supplier(id):
    conn=get_db(); conn.execute("DELETE FROM suppliers WHERE id=?",(id,)); conn.commit(); conn.close()

# ----- customers -----
def save_customer(name,contact,email,address):
    conn=get_db(); cur=conn.execute("INSERT INTO customers (customer_name,contact_number,email,address) VALUES (?,?,?,?)",(name,contact,email,address)); conn.commit(); nid=cur.lastrowid; conn.close(); return nid

def get_customer(id):
    conn=get_db(); r=conn.execute("SELECT * FROM customers WHERE id=?",(id,)).fetchone(); conn.close(); return dict(r) if r else None

def list_customers():
    conn=get_db(); rows=conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall(); conn.close(); return [dict(r) for r in rows]

def update_customer(id,name,contact,email,address):
    conn=get_db(); conn.execute("UPDATE customers SET customer_name=?,contact_number=?,email=?,address=? WHERE id=?",(name,contact,email,address,id)); conn.commit(); conn.close()

def delete_customer(id):
    conn=get_db(); conn.execute("DELETE FROM customers WHERE id=?",(id,)); conn.commit(); conn.close()

# ----- sales -----
def save_sale(transaction_date,customer_id,cashier,total_amount,payment_method,status,items):
    conn=get_db()
    cur=conn.execute("INSERT INTO sales (transaction_date,customer_id,cashier,total_amount,payment_method,status) VALUES (?,?,?,?,?,?)",(transaction_date,customer_id,cashier,total_amount,payment_method,status))
    sale_id=cur.lastrowid
    for it in items:
        conn.execute("INSERT INTO sale_items (sale_id,medicine_id,quantity,unit_price,subtotal) VALUES (?,?,?,?,?)",(sale_id, it["medicine_id"], it["quantity"], it["unit_price"], it["quantity"]*it["unit_price"]))
        # reduce stock
        conn.execute("UPDATE medicines SET quantity = quantity - ? WHERE id=?",(it["quantity"], it["medicine_id"]))
    conn.commit(); conn.close(); return sale_id

def get_sale(id):
    conn=get_db()
    sale=conn.execute("SELECT * FROM sales WHERE id=?",(id,)).fetchone()
    if not sale:
        conn.close(); return None
    items=conn.execute("SELECT * FROM sale_items WHERE sale_id=?",(id,)).fetchall()
    conn.close()
    d=dict(sale); d["items"]=[dict(r) for r in items]; return d

def list_sales():
    conn=get_db(); rows=conn.execute("SELECT * FROM sales ORDER BY id DESC").fetchall(); conn.close(); return [dict(r) for r in rows]

def update_sale_status(id,status):
    conn=get_db(); conn.execute("UPDATE sales SET status=? WHERE id=?",(status,id)); conn.commit(); conn.close()
