# Validation & Defense

## Standardized Error Shape
The team has agreed on the following JSON shape for all validation failures:
```json
{
  "status": 422,
  "error": "human-readable error message",
  "field": "name_of_the_invalid_field"
}
```

## Validation Matrix

| Route | Field | Rules |
|---|---|---|
| `POST/PUT /api/medicines` | `medicine_name` | required, string, presence |
| `POST/PUT /api/medicines` | `selling_price` | required, number (int/float), >= 0 |
| `POST/PUT /api/medicines` | `cost_price` | required, number (int/float), >= 0 |
| `POST/PUT /api/medicines` | `current_stock` | required, integer, >= 0 |
| `POST/PUT /api/medicines` | `status` | **derived** from `current_stock` via DB trigger; input is ignored |
| `POST/PUT /api/customers` | `customer_name` | required, string, presence |
| `POST/PUT /api/suppliers` | `supplier_name` | required, string, presence |
| `POST/PUT /api/sales` | `total_amount` | required, number, >= 0 |
| `POST/PUT /api/sales` | `cashier` | required, string, presence |

## Authorization Guards
- **Every route** (UI and `/api/*`) requires a logged-in session; UI pages redirect to `/login` and API calls return `401`.
- `DELETE /api/medicines/<id>`: requires the `Administrator` role in the session. Returns `403 Forbidden` otherwise.
- State-changing requests (POST/PUT/DELETE) require a valid CSRF token via the `X-CSRFToken` header or the `csrf_token` form field; otherwise `400`.

## Break-it Test Log (Task 5)
*Sent deliberately bad requests to confirm guard clauses are catching failures instead of crashing (500).*

1. **Missing required field**
   - Request: `POST /api/medicines/` with body `{"selling_price": 5.0}`
   - Result: `422 Unprocessable Entity`
   - Response: `{"status": 422, "error": "medicine_name is required", "field": "medicine_name"}`
   
2. **Wrong type**
   - Request: `POST /api/medicines/` with body `{"medicine_name": "Panadol", "selling_price": "five dollars", "cost_price": 2, "current_stock": 10}`
   - Result: `422 Unprocessable Entity`
   - Response: `{"status": 422, "error": "selling_price must be a positive number", "field": "selling_price"}`

3. **Out-of-range value**
   - Request: `POST /api/medicines/` with body `{"medicine_name": "Panadol", "selling_price": 5, "cost_price": 2, "current_stock": -5}`
   - Result: `422 Unprocessable Entity`
   - Response: `{"status": 422, "error": "current_stock must be a positive integer", "field": "current_stock"}`

4. **Invalid allowed value (enum)**
   - Request: `POST /api/medicines/` with body `{"medicine_name": "Panadol", "selling_price": 5, "cost_price": 2, "current_stock": 10, "status": "Pending"}`
   - Result: `422 Unprocessable Entity`
   - Response: `{"status": 422, "error": "invalid status", "field": "status"}`

5. **Forbidden action**
   - Request: `DELETE /api/medicines/1` (without headers)
   - Result: `403 Forbidden`
   - Response: `{"status": 403, "error": "not allowed, admin only"}`

*(All bad requests were caught gracefully. Zero 500 errors recorded.)*
