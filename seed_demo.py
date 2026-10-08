"""Demo dataset generator, shared by the local seed and serverless bootstraps.

`seed_all()` mirrors what the original seed.py created: ten categories, an
admin plus staff accounts, supplier and customer directories, a ten-medicine
catalog, ten sales with line items, ten purchases and ten adjustments — with
realistic stock arithmetic.

Why this lives in its own module: on Vercel every cold start gets a fresh
empty /tmp database, and `ensure_schema()` calls `seed_all()` exactly once
per brand-new database so the deployed demo is instantly presentable.

Passwords are hashed (never plaintext); the admin credentials can be
overridden with ADMIN_USERNAME / ADMIN_PASSWORD.
"""

import os
import random
import datetime

from controllers.security import hash_password

CATEGORIES = (
    ('Analgesics', 'Pain relievers'), ('Antibiotics', 'Bacterial infections'),
    ('Antipyretics', 'Fever reducers'), ('Antihistamines', 'Allergies'),
    ('Vitamins', 'Dietary supplements'), ('Antacids', 'Heartburn and indigestion'),
    ('Antiseptics', 'Infection prevention'), ('Cardiovascular', 'Heart conditions'),
    ('Dermatological', 'Skin care'), ('Respiratory', 'Breathing issues'),
)

SUPPLIERS = [
    (f'Supplier {i}', f'Contact {i}', f'555-010{i}', f'contact{i}@supplier.com',
     f'{i} Industrial Way', 'Active') for i in range(1, 11)
]

CUSTOMERS = [
    (f'Customer {i}', f'555-020{i}', f'customer{i}@mail.com', f'{i} Main St', 'Active')
    for i in range(1, 11)
]

MEDICINES = (
    ('Paracetamol 500mg', 'Paracetamol', 'Analgesics', 'Tablet', 5.0, 2.0, 1000),
    ('Amoxicillin 250mg', 'Amoxicillin', 'Antibiotics', 'Capsule', 15.0, 8.0, 500),
    ('Ibuprofen 400mg', 'Ibuprofen', 'Analgesics', 'Tablet', 8.0, 3.5, 800),
    ('Cetirizine 10mg', 'Cetirizine', 'Antihistamines', 'Tablet', 12.0, 5.0, 600),
    ('Vitamin C 500mg', 'Ascorbic Acid', 'Vitamins', 'Tablet', 4.0, 1.5, 2000),
    ('Omeprazole 20mg', 'Omeprazole', 'Antacids', 'Capsule', 25.0, 12.0, 400),
    ('Aspirin 81mg', 'Aspirin', 'Analgesics', 'Tablet', 3.0, 1.0, 1500),
    ('Loratadine 10mg', 'Loratadine', 'Antihistamines', 'Tablet', 10.0, 4.0, 750),
    ('Losartan 50mg', 'Losartan', 'Cardiovascular', 'Tablet', 20.0, 9.0, 300),
    ('Salbutamol Inhaler', 'Salbutamol', 'Respiratory', 'Inhaler', 150.0, 80.0, 50),
)


def bootstrap_admin(cursor):
    """Create the administrator account (overridable via env)."""
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
        (username, hash_password(password), 'Administrator'))


def seed_all(cursor):
    """Insert the full demo dataset. Intended for brand-new databases only.

    The caller commits. Medicine `status` is left to the DB triggers, which
    re-derive it whenever current_stock changes.
    """
    # 1. Categories
    cursor.executemany(
        'INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)',
        CATEGORIES)

    # 2. Users (admin + 10 staff)
    bootstrap_admin(cursor)
    staff = [((f'user{i}', 'password123', random.choice(['Staff', 'Pharmacist'])))
             for i in range(1, 11)]
    cursor.executemany(
        'INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
        [(u, hash_password(p), r) for (u, p, r) in staff])

    # 3. Suppliers
    cursor.executemany(
        'INSERT OR IGNORE INTO suppliers (supplier_name, contact_person, phone, email, address, status) '
        'VALUES (?, ?, ?, ?, ?, ?)', SUPPLIERS)

    # 4. Customers
    cursor.executemany(
        'INSERT OR IGNORE INTO customers (customer_name, phone, email, address, status) '
        'VALUES (?, ?, ?, ?, ?)', CUSTOMERS)

    # 5. Medicines (status derived by trigger from current_stock)
    cursor.executemany(
        'INSERT INTO medicines (medicine_name, generic_name, category, unit, '
        'selling_price, cost_price, current_stock) VALUES (?, ?, ?, ?, ?, ?, ?)',
        MEDICINES)

    # Snapshot rows so sales/purchases can move stock realistically.
    medicine_rows = {}
    for row in cursor.execute(
            'SELECT id, selling_price, cost_price, current_stock FROM medicines').fetchall():
        medicine_rows[row[0]] = {
            'selling_price': row[1], 'cost_price': row[2], 'stock': row[3]}
    medicine_ids = list(medicine_rows.keys())

    # 6. Sales (10) with line items; stock is decremented like a real checkout.
    for i in range(1, 11):
        dt = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
        lines = []
        total = 0.0
        for med_id in random.sample(medicine_ids, k=min(3, len(medicine_ids))):
            info = medicine_rows[med_id]
            if info['stock'] <= 0:
                continue
            qty = random.randint(1, min(10, info['stock']))
            info['stock'] -= qty
            subtotal = round(qty * info['selling_price'], 2)
            lines.append((med_id, qty, info['selling_price'], subtotal))
            total += subtotal

        if not lines:
            continue

        cursor.execute(
            'INSERT INTO sales (invoice_no, date_time, customer_id, cashier, total_amount, payment_method, status) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (f'INV-100{i}', dt, random.randint(1, 10), 'admin',
             round(total, 2), random.choice(['Cash', 'Card']), 'Completed'))
        sale_id = cursor.lastrowid
        cursor.executemany(
            'INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, subtotal) '
            'VALUES (?, ?, ?, ?, ?)',
            [(sale_id,) + line for line in lines])

    # 7. Purchases (10) with line items; received units go back into stock.
    for i in range(1, 11):
        dt = (datetime.datetime.now() - datetime.timedelta(days=i + 5)).strftime("%Y-%m-%d %H:%M:%S")
        lines = []
        total = 0.0
        for med_id in random.sample(medicine_ids, k=min(3, len(medicine_ids))):
            info = medicine_rows[med_id]
            qty = random.randint(5, 50)
            info['stock'] += qty
            subtotal = round(qty * info['cost_price'], 2)
            lines.append((med_id, qty, info['cost_price'], subtotal))
            total += subtotal

        if not lines:
            continue

        cursor.execute(
            'INSERT INTO purchases (supplier_id, date_time, total_amount, status) '
            'VALUES (?, ?, ?, ?)',
            (random.randint(1, 10), dt, round(total, 2), 'Completed'))
        purchase_id = cursor.lastrowid
        cursor.executemany(
            'INSERT INTO purchase_items (purchase_id, medicine_id, quantity, unit_cost, subtotal) '
            'VALUES (?, ?, ?, ?, ?)',
            [(purchase_id,) + line for line in lines])

    # 8. Adjustments (10)
    adjustments = []
    for i in range(1, 11):
        dt = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 20)))\
            .strftime("%Y-%m-%d %H:%M:%S")
        adjustments.append((random.randint(1, 10), random.randint(-20, -1), 'Expired/Damaged', dt))
    cursor.executemany(
        'INSERT INTO adjustments (medicine_id, qty, reason, date_time) VALUES (?, ?, ?, ?)',
        adjustments)

    # Persist the evolved stock levels so the numbers tell a coherent story.
    for med_id, info in medicine_rows.items():
        cursor.execute(
            'UPDATE medicines SET current_stock = ? WHERE id = ?',
            (info['stock'], med_id))