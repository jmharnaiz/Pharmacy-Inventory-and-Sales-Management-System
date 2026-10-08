# Bug Tracker & Triage

## BUG-001: XSS Vulnerability in Medicine Name
*   **Severity:** P0 (Security / Broken Core)
*   **Steps to reproduce:**
    1. Go to Add Medicine.
    2. Enter `<script>alert('hacked')</script>` as the Medicine Name.
    3. Fill out the rest of the form validly and save.
    4. View the Medicines List.
*   **Expected:** The input should be sanitized, rejected, or escaped upon rendering so the script does not execute.
*   **Actual:** The script executes immediately when the list page loads.

## BUG-002: SQLite Integer Overflow on Current Stock
*   **Severity:** P1 (Significant, has workaround - don't enter huge numbers)
*   **Steps to reproduce:**
    1. Go to Add Medicine.
    2. Enter `9999999999999999999` in the Current Stock field.
    3. Click Save.
*   **Expected:** The validation guard clause should cap the stock at a reasonable max integer (e.g., 999999) and return a 422.
*   **Actual:** The validation passes, but SQLite throws an `OverflowError` causing a 500 server crash.

## BUG-003: Double-click Submission creates Duplicate Records
*   **Severity:** P2 (Minor)
*   **Steps to reproduce:**
    1. Fill out the Add Medicine form.
    2. Rapidly double-click the "Save Medicine" button before the JS disable logic fires.
*   **Expected:** Only one record is created.
*   **Actual:** Two identical records are created in the database.
