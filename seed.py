"""Seed the database with demonstration data.

On a brand-new database `ensure_schema()` already seeds everything (so a
Vercel cold start or a wiped local DB is instantaneously usable). This script
tops up any remaining gaps and reports the result. It is safe to re-run.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import ensure_schema, get_db          # noqa: E402
from seed_demo import seed_all                 # noqa: E402


def main():
    ensure_schema()  # schema + admin + demo data when the DB is empty

    conn = get_db()
    medicines = conn.execute('SELECT COUNT(*) AS c FROM medicines').fetchone()['c']
    if medicines == 0:
        # Unusual state (users present but no catalog) — fill the gap.
        seed_all(conn.cursor())
        conn.commit()
        medicines = conn.execute('SELECT COUNT(*) AS c FROM medicines').fetchone()['c']
    sales = conn.execute('SELECT COUNT(*) AS c FROM sales').fetchone()['c']
    users = conn.execute('SELECT COUNT(*) AS c FROM users').fetchone()['c']
    conn.close()

    print('Database ready: %s users, %s medicines, %s sales.' % (users, medicines, sales))


if __name__ == '__main__':
    main()