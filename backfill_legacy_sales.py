"""Backfill line items for sales recorded before line items existed.

The sales table holds invoice totals but the original seed never wrote
per-medicine lines for them, so reports show zero cost of goods and the
sales list flags them as "legacy". Because the original item detail no
longer exists anywhere, this script reconstructs plausible lines from the
current medicine catalog whose subtotals add up to each invoice total.

Two guarantees keep the numbers honest:

1. Stock is never modified. Those units were already accounted for in each
   medicine's stock level when the sale was recorded — touching it now
   would double-count.
2. Each backfilled sale is flagged `legacy = 1`, which makes delete/edit
   skip the "return items to stock" step (the lines are estimates, not
   real units) and lets reports label cost of goods as an estimate.

Run it with:  python backfill_legacy_sales.py
It is idempotent: sales that already have line items are skipped.
"""
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import get_db, ensure_schema


def synthesize_items(total, meds, seed):
    """Build line items that sum to `total` using the medicine catalog.

    `meds` is a list of dicts with 'id' and 'selling_price'. The same seed
    always produces the same breakdown, so the backfill is reproducible.
    Returns a list of (medicine_id, quantity, unit_price, subtotal) tuples.
    """
    rng = random.Random(seed)
    remaining = round(float(total), 2)
    lines = []

    for _ in range(12):
        if remaining < 0.005:
            break
        affordable = [m for m in meds if m['selling_price'] <= remaining + 1e-9]
        if not affordable:
            break
        med = rng.choice(affordable)
        price = med['selling_price']
        max_qty = int(remaining / price)

        if max_qty * price <= remaining + 1e-9 and abs(max_qty * price - remaining) < 0.005:
            # This medicine fills the remainder exactly.
            qty = max_qty
        elif max_qty >= 2:
            # Leave at least a cent for the remaining lines.
            qty = rng.randint(1, max_qty - 1)
        else:
            qty = 1

        subtotal = round(qty * price, 2)
        lines.append((med['id'], qty, price, subtotal))
        remaining = round(remaining - subtotal, 2)

    if remaining >= 0.005:
        # Small leftover that no whole unit covers: one line priced at the
        # actual amount charged (a custom point-of-sale price).
        med = rng.choice(meds)
        leftover = round(remaining, 2)
        lines.append((med['id'], 1, leftover, leftover))

    return lines


def backfill_legacy_sales():
    """Insert line items for every sale that still has none.

    Returns the number of sales backfilled.
    """
    ensure_schema()
    conn = get_db()
    try:
        cursor = conn.cursor()
        meds = [dict(r) for r in cursor.execute(
            'SELECT id, medicine_name, selling_price FROM medicines').fetchall()]
        if not meds:
            return 0

        sales = cursor.execute(
            'SELECT id, invoice_no, total_amount FROM sales s '
            'WHERE NOT EXISTS (SELECT 1 FROM sale_items si WHERE si.sale_id = s.id) '
            'ORDER BY s.id'
        ).fetchall()

        for sale in sales:
            lines = synthesize_items(sale['total_amount'], meds, sale['id'])
            if not lines:
                continue
            cursor.executemany(
                'INSERT INTO sale_items (sale_id, medicine_id, quantity, unit_price, subtotal) '
                'VALUES (?, ?, ?, ?, ?)',
                [(sale['id'], med_id, qty, price, subtotal)
                 for (med_id, qty, price, subtotal) in lines]
            )
            cursor.execute('UPDATE sales SET legacy = 1 WHERE id = ?', (sale['id'],))

        conn.commit()
        return len(sales)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    count = backfill_legacy_sales()
    if count:
        print('Backfilled line items for %s legacy sale(s).' % count)
    else:
        print('No legacy sales to backfill.')


if __name__ == '__main__':
    main()