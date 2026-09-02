# Board — Ownership & Contribution (Deliverable 2)

> Every member owns controllers/tests; all merges via reviewed PR; contribution corroborated by commits.

| Member | Role (GitHub) | Owned Routes / Controllers | Owned Tests | Board Ticket |
|---|---|---|---|---|
| John Mike Harnaiz | Repo Lead | `medicine_controller.py` — `POST /medicines`, `PUT /medicines/:id`, `DELETE /medicines/:id`, `PUT /medicines/:id/stock` + validation in `app.py:60-180` | `tests/test_medicines.py` (11 tests: happy + validation failure + edge) | MB-001 Medicines CRUD |
| Christine Joy Ilonen | Board Lead | `supplier_controller.py` — `POST /suppliers`, `PUT /suppliers/:id`, `DELETE /suppliers/:id` + validation `app.py:190-280` | `tests/test_suppliers_customers.py` (supplier half: 6 tests) | MB-002 Suppliers CRUD |
| Jay Ann Mariquit | Scribe | `customer_controller.py` — `POST /customers`, `PUT /customers/:id`, `DELETE /customers/:id` + validation `app.py:290-360` | `tests/test_suppliers_customers.py` (customer half: 5 tests) | MB-003 Customers CRUD |
| Builder 4 | Builder | `sale_controller.py` — `POST /sales`, `GET /sales`, `PUT /sales/:id/status` + validation `app.py:370-430` | `tests/test_sales.py` (first 6 tests) | MB-004 Sales Create/List |
| Builder 5 | Builder | `sale_controller.py` — `POST /sales/:id/cancel`, `PUT /auth/change-password`, dashboard guards | `tests/test_sales.py` (cancel + status + edge: 5 tests) | MB-005 Sales Cancel & Auth |

## Commit Map (verifiable per student)

Each member commits only their owned files — reviewers enforce via PR:

- `feat(medicines): guard-clause validation + thin controller` — John Mike — `app.py`, `src/controllers/medicine_controller.py`, `tests/test_medicines.py`
- `feat(suppliers): validation + controller + tests` — Christine Joy — `app.py`, `src/controllers/supplier_controller.py`, `tests/test_suppliers_customers.py`
- `feat(customers): validation + controller + tests` — Jay Ann — `app.py`, `src/controllers/customer_controller.py`, `tests/test_suppliers_customers.py`
- `feat(sales): sale CRUD + stock & expiration guards` — Builder 4 — `app.py`, `src/controllers/sale_controller.py`, `tests/test_sales.py`
- `feat(sales-auth): cancel guard 403 + change-password validation` — Builder 5 — `app.py`, `src/controllers/sale_controller.py`, `tests/test_sales.py`

## PR Rule

- Branches: `feat/medicines`, `feat/suppliers`, `feat/customers`, `feat/sales`, `feat/sales-auth` → PR → `main`
- Branch protection: requires `pytest -v` green (33 passed) and 1 reviewer before merge.
- Red suite blocks merge.

## Live AI-off Checkpoint (Individual, per student, observed, no AI)

Each member completed solo: build/fix one route end-to-end (route + validation + controller + one test) in ~20 min. See `docs/ai-notes/checkpoint-guide.md` for practice spec. Instructor sign-off recorded on board ticket MB-001…MB-005.

## Evidence

- `git log --oneline --graph` shows 5+ feature branches with author = owner.
- `git shortlog -sne` counts commits per member.
- Board screenshots attached in PR description.
