# Binding Tests (Week 7)

## E2E Test Log for Medicine Form Binding

| Test Scenario | Action Performed | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| **Create Happy Path** | Filled form with valid data (Name: "Biogesic", Selling: 5, Cost: 2, Stock: 100), clicked Save. | Record persists, UI redirects to list, new record shows. | Form submitted via POST, spinner showed, redirected to `/ui/medicines`, Biogesic is visible in table. | ✅ PASS |
| **Edit Happy Path** | Clicked Edit on "Biogesic", changed Stock to 50, clicked Update. | `PUT` request sent to `/api/medicines/:id`. Redirects to list, stock is 50. | Form pre-filled correctly, spinner showed, PUT succeeded, list shows updated stock (50). | ✅ PASS |
| **Validation Failure (422)** | Attempted to create a medicine with Selling Price = `-5`. | Form does not redirect. 422 returned. Field-level error displays under Selling Price. | Spinner triggered then stopped. Error "selling_price must be a positive number" appeared directly under the Selling Price input field. | ✅ PASS |
| **General Failure (Network)** | Disconnected server while hitting Save. | General error banner displays "Network error." without crashing UI. | Catch block executed, red banner appeared at top of form. | ✅ PASS |

*All forms prevent default submission and handle the full async lifecycle (Loading, Success, Error).*
