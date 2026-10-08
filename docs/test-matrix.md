# Test Matrix & QA Pass (Week 10)

| Feature | Happy Path | Boundary (Huge #s) | Invalid (XSS/Emoji) | Empty / Missing | Permissions (User vs Admin) |
|---|---|---|---|---|---|
| **Medicines - Create** | ✅ PASS | ❌ FAIL (Stock > 2 billion crashes SQLite) | ❌ FAIL (Accepts `<script>` tags) | ✅ PASS (422 handled) | N/A |
| **Medicines - Read** | ✅ PASS | ✅ PASS | ✅ PASS | ✅ PASS (Empty state shows) | N/A |
| **Medicines - Update** | ✅ PASS | ✅ PASS | ❌ FAIL (Accepts `<script>` tags) | ✅ PASS (422 handled) | N/A |
| **Medicines - Delete** | ✅ PASS | N/A | N/A | ✅ PASS (404 handled) | ✅ PASS (403 enforced for non-admin) |
| **Customers - Create** | ✅ PASS | ✅ PASS | ✅ PASS (Emoji works fine) | ✅ PASS (422 handled) | N/A |
