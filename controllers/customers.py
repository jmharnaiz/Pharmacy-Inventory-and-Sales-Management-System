from db import get_db

def get_all_customers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_customer_by_id(customer_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_customer(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customers (customer_name, phone, email, address, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data.get('customer_name'),
        data.get('phone', ''),
        data.get('email', ''),
        data.get('address', ''),
        data.get('status', 'Active')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return get_customer_by_id(new_id)

def update_customer(customer_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE customers 
        SET customer_name = ?, phone = ?, email = ?, address = ?, status = ?
        WHERE id = ?
    ''', (
        data.get('customer_name'),
        data.get('phone', ''),
        data.get('email', ''),
        data.get('address', ''),
        data.get('status', 'Active'),
        customer_id
    ))
    conn.commit()
    conn.close()
    return get_customer_by_id(customer_id)

def delete_customer(customer_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# --- List search / sort / pagination ---------------------------------------

CUSTOMER_SORTS = {
    'name': 'customer_name ASC',
    'name_desc': 'customer_name DESC',
    'newest': 'id DESC',
}


def search_customers(q='', status='', sort='', page=1, per_page=10):
    """Filtered, sorted, paginated customers. Returns (rows, total)."""
    conn = get_db()
    where, params = [], []

    if q:
        where.append('(customer_name LIKE ? OR email LIKE ? OR phone LIKE ? OR address LIKE ?)')
        term = '%' + q + '%'
        params.extend([term, term, term, term])
    if status:
        where.append('status = ?')
        params.append(status)

    clause = (' WHERE ' + ' AND '.join(where)) if where else ''
    total = conn.execute('SELECT COUNT(*) AS c FROM customers' + clause, params).fetchone()['c']

    order = CUSTOMER_SORTS.get(sort, 'customer_name ASC')
    offset = (max(page, 1) - 1) * per_page
    rows = conn.execute(
        'SELECT * FROM customers' + clause + ' ORDER BY ' + order + ' LIMIT ? OFFSET ?',
        params + [per_page, offset]
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows], total
