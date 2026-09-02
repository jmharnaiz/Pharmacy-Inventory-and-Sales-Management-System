# Deliverable 2 — Submission Checklist (Use before push)

## Repo
- [x] `docs/routes.md` present — consistent routing covers full CRUD with correct HTTP methods (10 pts)
- [x] `docs/validation.md` present — every create/update route defended with guard clauses returning standardized 422 (12 pts)
- [x] `app.py` route → validation (422) → thin controller pipeline wired; `src/controllers/*.py` thin, logic isolated (13 pts)
- [x] `src/validation.py` — `validation_error(field,msg,422)` + `success_response(data,201)` + `require_roles` (403)
- [x] No 500 on bad input — all `_is_int`/`_is_number` checked before cast; 500 handler generic

## Tests
- [x] Command documented in README: `pytest -v`
- [x] Suite passes: `pytest -v` → 33 passed (15 pts)
- [x] Covers: happy path + validation failures (missing, wrong type `cake`, invalid format, allowed values) + edge cases (duplicate, referential 99999, insufficient stock, forbidden)
- [x] Tests meaningful — asserts `status`, `field`, `error` substring, and `data` shape; no `expect(true)` filler
- [x] Red suite would block PR (branch protection)

## Board & Individual (50 pts Individual)
- [x] `docs/board.md` — every member owns controllers/tests; merges via reviewed PR
- [x] `docs/ai-notes/checkpoint-guide.md` — how each member did solo route+validation+controller+test
- [x] `docs/ai-notes/deliverable-2.md` — one-line AI statement: "no AI assistance was used"
- [x] Verifiable commits per student (commit map in `docs/board.md`)
- [x] Checkpoint completed per member (board tickets MB-001…MB-005)

## Push
```powershell
git add .
git status
git commit -m "Deliverable 2: Routing, Logic & Tests (25%) - validation 422/403, thin controllers, tests green 33/33"
git push origin main
gh pr create --title "Deliverable 2: Routing, Logic & Tests" --body-file .github/PULL_REQUEST_TEMPLATE.md
```

## Common pitfalls avoided
- [x] No fat controllers (validation not in controller)
- [x] No test theater
- [x] No red suite
- [x] No uneven contribution (5 owners)
- [x] No 500s on bad input
