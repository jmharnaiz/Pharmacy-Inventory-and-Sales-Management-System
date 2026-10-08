import sqlite3
import os


def _default_db_path():
    # Vercel serverless functions only have a writable filesystem under /tmp,
    # and it is wiped on every cold start. Local development keeps a real file
    # next to the code.
    if os.environ.get('VERCEL') == '1':
        return os.path.join('/tmp', 'pharmacy.db')
    return os.path.join(os.path.dirname(__file__), 'pharmacy.db')


# Overridable via DATABASE_PATH (e.g. a mounted volume, or tests).
DATABASE_PATH = os.environ.get('DATABASE_PATH') or _default_db_path()


# ---- Remote (durable) database: Turso Cloud ----------------------------------
# When TURSO_DATABASE_URL (or the TURSO_URL alias) is set, every connection
# goes over HTTP to the hosted SQLite database instead of the local file.
# That is what makes edits and sales survive Vercel cold starts. Leave it
# unset to keep using the local `pharmacy.db` (local development).
TURSO_URL = (os.environ.get('TURSO_DATABASE_URL') or os.environ.get('TURSO_URL') or '').strip()
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN') or ''
USING_TURSO = bool(TURSO_URL)

# Persistent store preferences. Low-stock threshold is read by the stock
# status triggers, so this table must exist before they are created.
SETTINGS_TABLE = '''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
'''

DEFAULT_SETTINGS = (
    ('store_name', 'My Pharmacy Store'),
    ('currency', u'\u20b1'),          # default peso sign
    ('low_stock_threshold', '10'),
    ('invoice_prefix', 'INV-'),
)

# The base tables the app relies on. Kept in one place so both init_db()
# (full setup) and ensure_schema() (startup migration, including on a blank
# serverless database) create identical schemas.
BASE_TABLE_STATEMENTS = (
    SETTINGS_TABLE,
    '''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT NOT NULL,
            generic_name TEXT,
            category TEXT,
            unit TEXT,
            selling_price REAL NOT NULL,
            cost_price REAL NOT NULL,
            current_stock INTEGER NOT NULL,
            status TEXT DEFAULT 'In Stock'
        )
    ''',
    '''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            status TEXT DEFAULT 'Active'
        )
    ''',
    '''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            status TEXT DEFAULT 'Active'
        )
    ''',
    '''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT NOT NULL UNIQUE,
            date_time TEXT NOT NULL,
            customer_id INTEGER,
            cashier TEXT NOT NULL,
            total_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT DEFAULT 'Completed',
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''',
    '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''',
    '''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            description TEXT
        )
    ''',
    '''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY,
            supplier_id INTEGER,
            date_time TEXT,
            total_amount REAL,
            status TEXT,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        )
    ''',
    '''
        CREATE TABLE IF NOT EXISTS adjustments (
            id INTEGER PRIMARY KEY,
            medicine_id INTEGER,
            qty INTEGER,
            reason TEXT,
            date_time TEXT,
            FOREIGN KEY(medicine_id) REFERENCES medicines(id)
        )
    ''',
)

# Line-item tables are defined here so every caller can create them too.
LINE_ITEM_TABLES = (
    '''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (medicine_id) REFERENCES medicines (id)
        )
    ''',
    '''
        CREATE TABLE IF NOT EXISTS purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_cost REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (purchase_id) REFERENCES purchases (id),
            FOREIGN KEY (medicine_id) REFERENCES medicines (id)
        )
    ''',
)

# Stock status is derived from current_stock: the SQLite triggers keep the
# status column honest no matter which code path changes the stock level.
STOCK_STATUS_TRIGGERS = (
    '''
        CREATE TRIGGER IF NOT EXISTS trg_medicine_status_insert
        AFTER INSERT ON medicines
        FOR EACH ROW BEGIN
            UPDATE medicines SET status = CASE
                WHEN NEW.current_stock <= 0 THEN 'Out of Stock'
                WHEN NEW.current_stock <= IFNULL(
                    (SELECT CAST(value AS INTEGER) FROM settings WHERE key = 'low_stock_threshold'), 10
                ) THEN 'Low Stock'
                ELSE 'In Stock' END
            WHERE id = NEW.id;
        END
    ''',
    '''
        CREATE TRIGGER IF NOT EXISTS trg_medicine_status_update
        AFTER UPDATE OF current_stock ON medicines
        FOR EACH ROW BEGIN
            UPDATE medicines SET status = CASE
                WHEN NEW.current_stock <= 0 THEN 'Out of Stock'
                WHEN NEW.current_stock <= IFNULL(
                    (SELECT CAST(value AS INTEGER) FROM settings WHERE key = 'low_stock_threshold'), 10
                ) THEN 'Low Stock'
                ELSE 'In Stock' END
            WHERE id = NEW.id;
        END
    ''',
)


def get_db():
    """Open a database connection (local file, or Turso Cloud when set).

    The Turso driver mirrors the sqlite3 API — cursors, `?` placeholders,
    `row_factory`, `cursor.lastrowid`, `executemany` — so all controllers and
    routes work against either backend unchanged. Rows support both `row[0]`
    and `row['column_name']` access in both modes.
    """
    if USING_TURSO:
        # Import lazily: only required when a remote database is configured.
        import turso_serverless
        conn = turso_serverless.connect(TURSO_URL, auth_token=TURSO_AUTH_TOKEN or None)
        conn.row_factory = turso_serverless.Row
        return conn
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def integrity_errors():
    """Exception types for constraint violations (unique keys etc.).

    sqlite3 and the Turso driver define separate exception classes, so code
    that needs to catch them (e.g. duplicate invoice numbers) should use
    `except db.integrity_errors():` to work against both backends.
    """
    types = [sqlite3.IntegrityError]
    if USING_TURSO:
        try:
            import turso_serverless
            types.append(turso_serverless.IntegrityError)
        except ImportError:
            pass
    return tuple(types)


def _table_exists(cursor, name):
    return cursor.execute(
        'SELECT 1 FROM sqlite_master WHERE type = ? AND name = ?', ('table', name)
    ).fetchone() is not None


def _create_base_tables(cursor):
    for statement in BASE_TABLE_STATEMENTS + LINE_ITEM_TABLES:
        cursor.execute(statement)


def _add_sales_legacy_column(cursor):
    """Add the `legacy` flag that marks pre-line-item sales (migration)."""
    if 'legacy' not in [r['name'] for r in cursor.execute('PRAGMA table_info(sales)').fetchall()]:
        cursor.execute('ALTER TABLE sales ADD COLUMN legacy INTEGER NOT NULL DEFAULT 0')


def _seed_default_settings(cursor):
    cursor.executemany('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', DEFAULT_SETTINGS)


def _refresh_stock_statuses(cursor):
    """One-time recompute of status for rows that predate the triggers."""
    if not _table_exists(cursor, 'medicines'):
        return
    cursor.execute('''
        UPDATE medicines SET status = CASE
            WHEN current_stock <= 0 THEN 'Out of Stock'
            WHEN current_stock <= IFNULL(
                (SELECT CAST(value AS INTEGER) FROM settings WHERE key = 'low_stock_threshold'), 10
            ) THEN 'Low Stock'
            ELSE 'In Stock' END
    ''')


def _migrate_plaintext_passwords(cursor):
    """Hash any plaintext passwords still stored in the users table.

    The plaintext value is read from the row itself and replaced with a
    werkzeug scrypt hash, so existing accounts keep working.
    """
    if not _table_exists(cursor, 'users'):
        return
    from controllers.security import hash_password
    rows = cursor.execute('SELECT id, password FROM users').fetchall()
    for row in rows:
        # Werkzeug hashes always contain '$'; plaintext never does.
        if row['password'] and '$' not in row['password']:
            cursor.execute(
                'UPDATE users SET password = ? WHERE id = ?',
                (hash_password(row['password']), row['id'])
            )


def _bootstrap_if_empty(cursor):
    """Create the admin account and demo dataset on a brand-new database.

    Serverless deploys (Vercel) start every cold run with an empty /tmp
    database, so first use must be painless: an admin exists to log in and
    the demo catalog is populated just like the local seed.
    """
    if not _table_exists(cursor, 'users'):
        return
    if cursor.execute('SELECT COUNT(*) AS c FROM users').fetchone()['c'] > 0:
        return
    from seed_demo import seed_all
    seed_all(cursor)


def ensure_schema():
    """Create and migrate every table, idempotently, on startup.

    Safe to call on every launch — including against a blank serverless
    database: every statement is IF NOT EXISTS or guarded by a probe first.
    """
    conn = get_db()
    cursor = conn.cursor()
    _create_base_tables(cursor)
    _add_sales_legacy_column(cursor)
    for statement in STOCK_STATUS_TRIGGERS:
        cursor.execute(statement)
    _seed_default_settings(cursor)
    _bootstrap_if_empty(cursor)
    _refresh_stock_statuses(cursor)
    _migrate_plaintext_passwords(cursor)
    conn.commit()
    conn.close()


def init_db():
    """Full schema setup for a brand-new database file (used by tests and
    the local `python db.py`). Never seeds demo catalog data, so tests still
    see empty tables; the admin account is created with hashed credentials.
    """
    conn = get_db()
    cursor = conn.cursor()
    _create_base_tables(cursor)
    _add_sales_legacy_column(cursor)
    for statement in STOCK_STATUS_TRIGGERS:
        cursor.execute(statement)
    _seed_default_settings(cursor)
    # Default Admin (password hashed, never stored in plaintext) — env
    # overrides ADMIN_USERNAME / ADMIN_PASSWORD, defaults admin / admin123.
    from seed_demo import bootstrap_admin
    bootstrap_admin(cursor)
    _refresh_stock_statuses(cursor)
    _migrate_plaintext_passwords(cursor)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")