# AI Prompt Log (Week 10)

*AI use is ON for test scaffolding.*

**AI Assistant Used**: Antigravity (Gemini)

## 1. Scaffolding Adversarial Tests
**Prompt**: "Generate two automated pytest functions for our `test_medicines.py` suite targeting adversarial paths we discovered during manual QA. One test should try to inject an extremely large integer `9999999999999999999` to trigger the SQLite overflow bug. The second test should inject `<script>alert(1)</script>` to target the XSS vulnerability."
**Result**: AI generated the test scaffolding perfectly. I left the assertions commented out or passing temporarily with `pass` so that our suite remains "green" for this week (as per instructions: "find and log bugs, don't fix them yet"). These tests will be uncommented and used to drive the bug fixes in Week 11.

**Integrity Signature**: We designed the QA matrix manually and executed the adversarial sessions by hand. AI was only used to translate our findings into pytest scaffolding.
