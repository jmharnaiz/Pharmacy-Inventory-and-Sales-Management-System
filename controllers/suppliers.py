from db import get_db

def get_all_suppliers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM suppliers')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_supplier_by_id(supplier_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM suppliers WHERE id = ?', (supplier_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_supplier(data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO suppliers (supplier_name, contact_person, phone, email, address, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('supplier_name'),
        data.get('contact_person', ''),
        data.get('phone', ''),
        data.get('email', ''),
        data.get('address', ''),
        data.get('status', 'Active')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return get_supplier_by_id(new_id)

def update_supplier(supplier_id, data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE suppliers
        SET supplier_name = ?, contact_person = ?, phone = ?, email = ?, address = ?, status = ?
        WHERE id = ?
    ''', (
        data.get('supplier_name'),
        data.get('contact_person', ''),
        data.get('phone', ''),
        data.get('email', ''),
        data.get('address', ''),
        data.get('status', 'Active'),
        supplier_id
    ))
    conn.commit()
    conn.close()
    return get_supplier_by_id(supplier_id)

def delete_supplier(supplier_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# --- List search / sort / pagination ---------------------------------------

SUPPLIER_SORTS = {
    'name': 'supplier_name ASC',
    'name_desc': 'supplier_name DESC',
    'newest': 'id DESC',
}


def search_suppliers(q='', status='', sort='', page=1, per_page=10):
    """Filtered, sorted, paginated suppliers. Returns (rows, total)."""
    conn = get_db()
    where, params = [], []

    if q:
        where.append('(supplier_name LIKE ? OR contact_person LIKE ? OR phone LIKE ? OR email LIKE ?)')
        term = '%' + q + '%'
        params.extend([term, term, term, term])
    if status:
        where.append('status = ?')
        params.append(status)

    clause = (' WHERE ' + ' AND '.join(where)) if where else ''
    total = conn.execute('SELECT COUNT(*) AS c FROM suppliers' + clause, params).fetchone()['c']

    order = SUPPLIER_SORTS.get(sort, 'supplier_name ASC')
    offset = (max(page, 1) - 1) * per_page
    rows = conn.execute(
        'SELECT * FROM suppliers' + clause + ' ORDER BY ' + order + ' LIMIT ? OFFSET ?',
        params + [per_page, offset]
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows], total
