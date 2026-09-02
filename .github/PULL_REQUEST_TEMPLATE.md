# Pull Request — Deliverable 2

## Checklist (must be green before merge)
- [ ] `docs/routes.md` — consistent routing structure
- [ ] `docs/validation.md` — full matrix + break-it log; every create/update route has field-by-field rules
- [ ] Guard-clause validation on every create/update route, returning `422` on bad data (never 500)
- [ ] One consistent error shape: `{"status":422,"error":"...","field":"..."}`; auth `403`; no leaked stack traces
- [ ] At least one authorization guard returning `403` (delete medicine/supplier/customer, cancel sale)
- [ ] Thin controllers wired `route → validation → controller → db` and standardized success `{ "status":201, "data":{...}}`
- [ ] Tests: happy path + validation failure + edge for each controller; `pytest -v` green
- [ ] No AI used this phase — confirm honestly

## Tests
```
pytest -v
```

## Screenshot of green suite
(paste)
