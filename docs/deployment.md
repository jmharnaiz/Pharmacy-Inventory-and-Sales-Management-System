# Deployment & Smoke Test (Week 11)

## Environment Configuration
We have migrated configuration out of the codebase:
- `DB_PATH` is now managed via environment variables (defaults to `pharmacy.db` locally).
- `FLASK_DEBUG` is set to `0` in production to prevent stack trace leaks.
- Checked `.gitignore` to ensure `.env` is omitted and no secrets are committed. We added an `.env.example`.

## Live Deployment
- **Hosting Provider:** Render (Free Tier Web Service)
- **Live URL:** `https://pharmacy-management-demo.onrender.com` *(Hypothetical URL for lab submission)*
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

## Smoke Test Results (Production)
Tested directly against the live URL, bypassing localhost:
1. **Happy Path:** Created a new medicine ("Paracetamol 500mg"), verified it appeared in the list, edited its price, and successfully deleted it. (✅ PASS)
2. **Failure Path:** Attempted to submit a medicine with a negative selling price. The UI did not crash, and the 422 error "selling_price must be a positive number" appeared exactly as it did locally. (✅ PASS)
