from db import get_db

def get_all_medicines():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM medicines')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_medicine_by_id(medicine_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM medicines WHERE id = ?', (medicine_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_medicine(data):
    # `status` is derived from current_stock by a DB trigger — never from input.
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medicines (medicine_name, generic_name, category, unit, selling_price, cost_price, current_stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('medicine_name'),
        data.get('generic_name', ''),
        data.get('category', ''),
        data.get('unit', ''),
        data.get('selling_price'),
        data.get('cost_price'),
        data.get('current_stock')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return get_medicine_by_id(new_id)

def update_medicine(medicine_id, data):
    # `status` is derived from current_stock by a DB trigger — never from input.
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE medicines 
        SET medicine_name = ?, generic_name = ?, category = ?, unit = ?, selling_price = ?, cost_price = ?, current_stock = ?
        WHERE id = ?
    ''', (
        data.get('medicine_name'),
        data.get('generic_name', ''),
        data.get('category', ''),
        data.get('unit', ''),
        data.get('selling_price'),
        data.get('cost_price'),
        data.get('current_stock'),
        medicine_id
    ))
    conn.commit()
    conn.close()
    return get_medicine_by_id(medicine_id)

def delete_medicine(medicine_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM medicines WHERE id = ?', (medicine_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# --- List search / sort / pagination ---------------------------------------

LOW_STOCK_THRESHOLD = 10

# Whitelisted ORDER BY clauses: values are literals, never user input.
MEDICINE_SORTS = {
    'name': 'medicine_name ASC',
    'name_desc': 'medicine_name DESC',
    'stock': 'current_stock ASC',
    'stock_desc': 'current_stock DESC',
    'price': 'selling_price ASC',
    'price_desc': 'selling_price DESC',
}


def search_medicines(q='', category='', sort='', page=1, per_page=10):
    """Filtered, sorted, paginated medicines. Returns (rows, total)."""
    conn = get_db()
    where, params = [], []

    if q:
        where.append('(medicine_name LIKE ? OR generic_name LIKE ? OR category LIKE ?)')
        term = '%' + q + '%'
        params.extend([term, term, term])
    if category:
        where.append('category = ?')
        params.append(category)

    clause = (' WHERE ' + ' AND '.join(where)) if where else ''
    total = conn.execute('SELECT COUNT(*) AS c FROM medicines' + clause, params).fetchone()['c']

    order = MEDICINE_SORTS.get(sort, 'medicine_name ASC')
    offset = (max(page, 1) - 1) * per_page
    rows = conn.execute(
        'SELECT * FROM medicines' + clause + ' ORDER BY ' + order + ' LIMIT ? OFFSET ?',
        params + [per_page, offset]
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows], total


def list_categories():
    conn = get_db()
    rows = conn.execute(
        'SELECT DISTINCT category FROM medicines WHERE category IS NOT NULL AND category != ? ORDER BY category',
        ('',)
    ).fetchall()
    conn.close()
    return [row['category'] for row in rows]
