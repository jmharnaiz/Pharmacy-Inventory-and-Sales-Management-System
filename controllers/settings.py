from db import get_db, DEFAULT_SETTINGS

DEFAULT_MAP = dict(DEFAULT_SETTINGS)


def get_setting(key, default=None):
    """Return one stored setting, falling back to its default value."""
    conn = get_db()
    row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
    conn.close()
    if row is not None:
        return row['value']
    return default if default is not None else DEFAULT_MAP.get(key)


def get_settings():
    """Return all settings as a dict (missing keys fall back to defaults)."""
    conn = get_db()
    rows = conn.execute('SELECT key, value FROM settings').fetchall()
    conn.close()
    stored = {r['key']: r['value'] for r in rows}
    merged = dict(DEFAULT_MAP)
    merged.update(stored)
    return merged


def save_settings(values):
    """Upsert the given {key: value} pairs into the settings table."""
    conn = get_db()
    try:
        for key, value in values.items():
            conn.execute(
                'INSERT INTO settings (key, value) VALUES (?, ?) '
                'ON CONFLICT(key) DO UPDATE SET value = excluded.value',
                (key, str(value)))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def int_setting(key, default):
    """Convenience: parse an integer setting defensively."""
    raw = get_setting(key, default)
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default