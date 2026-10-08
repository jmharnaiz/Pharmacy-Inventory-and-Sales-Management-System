# AI Prompt Log (Week 11)

*AI use is ON. Focus is on reviewing AI fixes.*

**AI Assistant Used**: Antigravity (Gemini)

## 1. Squashing P0/P1 Bugs
**Prompt**: "I need to fix two bugs in our `routes/medicines.py` validation guard. Bug 1: It accepts `<script>` tags causing an XSS risk. Bug 2: `current_stock` accepts integers larger than a 32-bit max, causing a SQLite overflow. Please update the `validate_medicine` function to reject `<script>` and `</script>`, and to cap `current_stock` at `2147483647`."
**Result**: The AI successfully updated the guard clause. I carefully reviewed the logic (since we are near release) and confirmed it correctly returns our standard `422` envelope for both cases, preventing the bugs before they reach the database or the client UI.

**Integrity Signature**: I uncommented the adversarial tests from Week 10, ran `pytest`, and confirmed the suite went from failing to green. The bug fixes were reviewed before merging.
