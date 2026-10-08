# Find the Flaw (Week 9)

As part of the Week 9 peer review exercise, we generated an AI-assisted snippet to handle adding a new "Category" to the system, intentionally not reviewing it perfectly before proposing the PR.

## Snippet 1: AI-Generated `Categories` POST Route
**The Proposed Code:**
```python
@categories_bp.route('/', methods=['POST'])
def add_category():
    data = request.json
    if not data['category_name']:
        return jsonify({"error": "Missing name"}), 400
    
    # Save to db...
    db.execute('INSERT INTO categories (name) VALUES (?)', data['category_name'])
    return jsonify({"success": True}), 200
```

## Flaws Identified During Review:
1. **Unhandled 500 Crash (KeyError)**: If the client sends an empty JSON payload or a payload without the `'category_name'` key, `data['category_name']` will throw a Python `KeyError`. This bypasses our guard clauses and crashes the server. *Fix: Use `data.get('category_name')`.*
2. **Inconsistent Error Shape**: Returns `{"error": "Missing name"}`. This violates our Week 4 standard. *Fix: It must return `{"status": 422, "error": "Missing name", "field": "category_name"}`.*
3. **Wrong Status Codes**: It returns a `400` for validation instead of our agreed `422`, and it returns `200` for creation instead of `201 Created`.
4. **SQL Execution Bug**: `db.execute` expects a tuple for parameterized queries. Passing a string directly will cause SQLite to treat the string as a sequence of characters, leading to a "bindings count mismatch" 500 error. *Fix: Pass `(data.get('category_name'),)`.*

## Review Feedback (Task 4)
*   **[blocking]** "Good start on the route! However, accessing the dictionary directly via `data['category_name']` will crash the server with a 500 if the payload is empty. Please change this to `data.get('category_name')`."
*   **[blocking]** "The error response shape doesn't match our agreed project format. Please update the error return to match our envelope: `{'status': 422, 'error': '...', 'field': 'category_name'}`."
*   **[nit]** "Let's change the success status code from 200 to 201 to properly match REST conventions for resource creation."
