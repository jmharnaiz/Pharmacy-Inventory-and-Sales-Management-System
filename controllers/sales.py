from db import get_db


class SaleError(Exception):
    """Domain error raised while writing a sale.

    Carries the HTTP status and form field the route should report the
    message against, so routes can translate it into the standard
    {"status": ..., "error": ..., "field": ...} response shape.
    """

    def __init__(self, message, field='items', status=422):
        super().__init__(message)
        self.message = message
        self.field = field
        self.status = status


def get_all_sales():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sales.*, customers.customer_name 
        FROM sales 
        LEFT JOIN customers ON sales.customer_id = customers.id
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_sale_by_id(sale_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sales.*, customers.customer_name 
        FROM sales 
        LEFT JOIN customers ON sales.customer_id = customers.id
        WHERE sales.id = ?
    ''', (sale_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_sale_items(sale_id):
    conn = get_db()
    rows = conn.execute('''
        SELECT sale_items.*, medicines.medicine_name
        FROM sale_items
        LEFT JOIN medicines ON medicines.id = sale_items.medicine_id
        WHERE sale_items.sale_id = ?
        ORDER BY sale_items.id
    ''', (sale_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_sale(data):
    """Insert a sale with its line items and decrement stock, atomically.

    Either the sale, all of its items and all stock updates land, or none
    of them do.
    """
    items = data.get('items') or []
    if not items:
        raise SaleError('a sale requires at least one line item', field='items')

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sales (invoice_no, date_time, customer_id, cashier, total_amount, payment_method, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('invoice_no'),
            data.get('date_time'),
            _clean_customer_id(data.get('customer_id')),
            data.get('cashier', 'Admin'),
            0,
            data.get('payment_method'),
            data.get('status', 'Completed')
        ))
        sale_id = cursor.lastrowid

        total = _write_items(cursor, sale_id, items)
        cursor.execute('UPDATE sales SET total_amount = ? WHERE id = ?', (round(total, 2), sale_id))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return get_sale_by_id(sale_id)


def update_sale(sale_id, data):
    """Update a sale header, and its line items when `items` is supplied.

    When items are supplied the previous lines are returned to stock first
    and the new lines applied, so editing a sale reconciles inventory.
    """
    items = data.get('items')

    conn = get_db()
    try:
        cursor = conn.cursor()
        existing = cursor.execute('SELECT * FROM sales WHERE id = ?', (sale_id,)).fetchone()
        if not existing:
            raise SaleError('Sale not found.', field='id', status=404)

        # Only overwrite columns the caller actually sent, so a partial
        # payload (the edit form sends customer/payment/items only) keeps
        # the invoice number and timestamp it already had.
        def value_for(key, default):
            return data[key] if key in data and data[key] != '' else default

        customer_id = (_clean_customer_id(data['customer_id']) if 'customer_id' in data
                       else existing['customer_id'])

        cursor.execute('''
            UPDATE sales
            SET invoice_no = ?, date_time = ?, customer_id = ?, cashier = ?, payment_method = ?, status = ?
            WHERE id = ?
        ''', (
            value_for('invoice_no', existing['invoice_no']),
            value_for('date_time', existing['date_time']),
            customer_id,
            value_for('cashier', existing['cashier']),
            value_for('payment_method', existing['payment_method']),
            value_for('status', existing['status']),
            sale_id
        ))

        if items is None:
            # Legacy payload without line items: trust the supplied total.
            if data.get('total_amount') is not None:
                cursor.execute('UPDATE sales SET total_amount = ? WHERE id = ?',
                               (data.get('total_amount'), sale_id))
        else:
            if not items:
                raise SaleError('a sale requires at least one line item', field='items')
            # A backfilled (legacy) sale's lines are estimates derived from the
            # stored total, so they were never taken from stock — don't return
            # them. Once real lines are written the sale becomes a normal one.
            if not existing['legacy']:
                _restock(cursor, sale_id)
            cursor.execute('DELETE FROM sale_items WHERE sale_id = ?', (sale_id,))
            total = _write_items(cursor, sale_id, items)
            cursor.execute('UPDATE sales SET total_amount = ?, legacy = 0 WHERE id = ?',
                           (round(total, 2), sale_id))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return get_sale_by_id(sale_id)


def delete_sale(sale_id):
    """Delete a sale and return its line items to stock.

    Backfilled (legacy) sales keep their synthesized lines in the database
    only, so deleting one never moves stock.
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        row = cursor.execute('SELECT legacy FROM sales WHERE id = ?', (sale_id,)).fetchone()
        if not row:
            return False
        if not row['legacy']:
            _restock(cursor, sale_id)
        cursor.execute('DELETE FROM sale_items WHERE sale_id = ?', (sale_id,))
        cursor.execute('DELETE FROM sales WHERE id = ?', (sale_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _write_items(cursor, sale_id, items):
    """Insert line items and decrement stock. Returns the computed total.

    The stock update is a single guarded UPDATE, so two concurrent sales
    can never both take the last unit.
    """
    total = 0.0
    for item in items:
        medicine_id = item.get('medicine_id')
        quantity = item.get('quantity')

        medicine = cursor.execute(
            'SELECT id, medicine_name, selling_price, current_stock FROM medicines WHERE id = ?',
            (medicine_id,)
        ).fetchone()
        if not medicine:
            raise SaleError('medicine %s does not exist' % medicine_id, field='items')

        cursor.execute(
            'UPDATE medicines SET current_stock = current_stock - ? WHERE id = ? AND current_stock >= ?',
            (quantity, medicine_id, quantity)
        )
        if cursor.rowcount != 1:
            raise SaleError(
                'insufficient stock for %s: only %s left' % (medicine['medicine_name'], medicine['current_stock']),
                field='items'
            )

        unit_price = item.get('unit_price')
        if unit_price is None:
            unit_price = medicine['selling_price']

        subtotal = round(unit_price * quantity, 2)
        cursor.execute('''
            INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?)
        ''', (sale_id, medicine_id, quantity, unit_price, subtotal))
        total += subtotal

    return total


def _restock(cursor, sale_id):
    """Return every line item of a sale to its medicine's stock."""
    rows = cursor.execute(
        'SELECT medicine_id, quantity FROM sale_items WHERE sale_id = ?',
        (sale_id,)
    ).fetchall()
    for row in rows:
        cursor.execute(
            'UPDATE medicines SET current_stock = current_stock + ? WHERE id = ?',
            (row['quantity'], row['medicine_id'])
        )


def _clean_customer_id(raw):
    """Normalise the customer id: blank means walk-in, non-numeric is invalid."""
    if raw is None or raw == '' or raw == 'None':
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise SaleError('customer_id must be an integer', field='customer_id', status=422)


# --- List search / sort / pagination ---------------------------------------

SALE_SORTS = {
    'newest': 'sales.date_time DESC',
    'oldest': 'sales.date_time ASC',
    'total_desc': 'sales.total_amount DESC',
    'total_asc': 'sales.total_amount ASC',
    'invoice': 'sales.invoice_no ASC',
}


def search_sales(q='', sort='', page=1, per_page=10):
    """Filtered, sorted, paginated sales with customer name and line count.

    Returns (rows, total).
    """
    conn = get_db()
    where, params = [], []

    if q:
        where.append('(sales.invoice_no LIKE ? OR customers.customer_name LIKE ? OR sales.cashier LIKE ?)')
        term = '%' + q + '%'
        params.extend([term, term, term])

    where_sql = (' WHERE ' + ' AND '.join(where)) if where else ''
    join_sql = ' LEFT JOIN customers ON customers.id = sales.customer_id'

    total = conn.execute(
        'SELECT COUNT(*) AS c FROM sales' + join_sql + where_sql, params
    ).fetchone()['c']

    order = SALE_SORTS.get(sort, 'sales.date_time DESC')
    offset = (max(page, 1) - 1) * per_page
    rows = conn.execute(
        'SELECT sales.*, customers.customer_name AS customer_name, '
        " (SELECT COUNT(*) FROM sale_items WHERE sale_id = sales.id) AS item_count "
        'FROM sales' + join_sql + where_sql +
        ' ORDER BY ' + order + ' LIMIT ? OFFSET ?',
        params + [per_page, offset]
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows], total
