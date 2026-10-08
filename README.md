# Pharmacy Inventory and Sales Management System

## Project Description
A local pharmacy needs a system to manage their medicines inventory, track sales, and maintain records of their customers and suppliers. This system will allow pharmacists and cashiers to perform CRUD operations on medicines, process sales, and ensure stock levels are monitored.

## Team Roster & Roles
- **Repo Lead:** Antigravity (AI)
- **Board Lead:** Antigravity (AI)
- **Scribe:** Antigravity (AI)
- **Builders:** Antigravity (AI), User

## Record Types (Entities)
1. **Medicines**: Products sold in the pharmacy.
2. **Customers**: Registered clients.
3. **Suppliers**: Pharmaceutical distributors.
4. **Sales**: Transaction records mapping customers to purchased medicines.

## Running Locally

```powershell
python db.py            # create the schema (optional; app auto-migrates too)
python seed.py          # load demo data (optional; fresh DBs bootstrap themselves)
python app.py           # start the dev server on http://127.0.0.1:5000
```

Sign in with `admin` / `admin123` (change it via the `ADMIN_USERNAME` /
`ADMIN_PASSWORD` env vars on a fresh database).

Tests: `python -m pytest tests -q`

## Deploying to Vercel (durable data)

The repo is configured for Vercel serverless, and data lives on **Turso** —
hosted SQLite reached over HTTP — so everything you edit, sell, or add
**persists across refreshes and cold starts**. Locally the app keeps using the
file database automatically; Turso activates only when `TURSO_DATABASE_URL`
is set.

What makes this work:

- `vercel.json` — routes every request to the Python function.
- `api/index.py` — WSGI entry point exposing the Flask app.
- `db.py` — `get_db()` speaks to Turso when `TURSO_DATABASE_URL` is set and
  to the local file otherwise; the Turso driver mirrors the `sqlite3` API
  (`?` placeholders, `row['name']`, `cursor.lastrowid`, `executemany`), so no
  query code changes.
- `seed_demo.py` — a first-boot bootstrap: the very first request to a fresh
  Turso database creates the admin account plus a full demo catalog.
- `.vercelignore` — keeps the local `pharmacy.db`, secrets and docs out of the
  function bundle.

Steps:

1. Create a free Turso database (one-time):
   ```powershell
   npm i -g @turso/cli
   turso auth login
   turso db create pharmacy
   turso db show pharmacy --url          # the libsql://... URL
   turso db tokens create pharmacy       # the auth token
   ```
2. From this folder: `vercel login` then `vercel --prod`
3. Add project environment variables in the Vercel dashboard:
   - `TURSO_DATABASE_URL` — the `libsql://...` URL from step 1 (**required**).
   - `TURSO_AUTH_TOKEN` — the token from step 1 (**required**).
   - `SECRET_KEY` — a long random hex string (**required**; without it every
     cold start signs everyone out because the session key changes).
   - `ADMIN_USERNAME` / `ADMIN_PASSWORD` — first-boot admin credentials
     (optional; defaults to `admin` / `admin123`).
4. Open the deployed URL and sign in.

> **Without Turso env vars the deploy still works, but data resets:** Vercel
> serverless only has a writable `/tmp`, wiped on every cold start, so the DB
> falls back to `/tmp/pharmacy.db` (demo-grade). Setting `TURSO_DATABASE_URL`
> is what makes records durable.
