# Feedback Tests (Week 8)

| Scenario | Action Performed | Expected Feedback | Actual Feedback | Status |
|---|---|---|---|---|
| **Invalid Data Submit** | Created medicine with negative selling price | Inline field error under selling price input, no crash | Red text appeared: "selling_price must be a positive number". | ✅ PASS |
| **Record Not Found** | Navigated to `/ui/medicines/999/edit` | 404 state is handled, user sees clear error | Screen loaded with red banner at the top: "Medicine not found". | ✅ PASS |
| **Delete Confirmation** | Clicked delete on medicine row | Modal/Alert confirms destruction before proceeding | Browser confirm prompt appeared: "Are you sure you want to delete this medicine?" | ✅ PASS |
| **Unauthorized Delete** | Removed the 'Bearer admin-token' from JS fetch and clicked Delete | 403 Forbidden handled gracefully | JS caught the 403 and `alert()` showed: "Failed to delete: not allowed, admin only". Icon reverted from spinner to trash can. | ✅ PASS |
| **Network Failure** | Disconnected internet, hit save | General failure message, UI doesn't freeze | Top error banner showed "Network error. Please try again." Button re-enabled. | ✅ PASS |
