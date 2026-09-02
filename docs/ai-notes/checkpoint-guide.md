# AI-off Checkpoint Guide (Individual, ~20 min) — Week 5 Task 4

Each member builds or fixes a single route end-to-end against a short spec, solo, no AI.

## Practice spec (example you may get)

> Add `POST /medicines` validation for `expiration_date` must be future date, or fix `DELETE /medicines/:id` to check `require_roles("Admin")` and return 403 for non-Admin.

## Steps

1. **Route**: add `@app.route("/medicines", methods=["POST"])` + `@login_required`
2. **Validation** (guard clauses at top, return early):
   ```python
   if not name: return validation_error("medicine_name","medicine_name is required")
   if not _is_int(qty): return validation_error("quantity","quantity must be a number")
   if int(qty)<0 or int(qty)>99999: return validation_error("quantity","quantity out of range (0-99999)")
   if not is_valid_date_ymd(exp): return validation_error("expiration_date","expiration_date must be YYYY-MM-DD format")
   ```
3. **Controller** (thin, no validation):
   ```python
   validated={...}
   return create_medicine_controller(validated)
   ```
   Controller in `src/controllers/medicine_controller.py`:
   ```python
   def create_medicine_controller(validated):
       nid = save_medicine(...)
       return success_response(get_medicine(nid), 201)
   ```
4. **Test** (Arrange–Act–Assert):
   ```python
   def test_createMedicine_rejects_cake():
       init_db()
       with app.test_client() as c:
           login(c)
           resp=c.post("/medicines", json={...,"quantity":"cake"})
           assert resp.status_code==422
           assert resp.get_json()["field"]=="quantity"
   ```

## What the instructor checks
- Guard clauses at top, not scattered; 422 on bad data, never 500; 403 distinct from 422; success `{status:201, data:...}`

## Board ownership
Each member owns at least one controller + its tests; all merges via reviewed PR; red suite blocks PR.
