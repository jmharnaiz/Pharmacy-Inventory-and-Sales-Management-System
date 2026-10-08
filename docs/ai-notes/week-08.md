# AI Prompt Log (Week 8)

*AI use is ON and required for this phase.*

**AI Assistant Used**: Antigravity (Gemini)

## 1. Scaffolding Delete Lifecycle
**Prompt**: "Write a JavaScript function `deleteMedicine(id, btnElement)` to handle deleting a row from the list. It needs to show a confirmation dialog first. Then, set the button icon to a spinner and disable it. Send a DELETE fetch request. If successful, fade out and remove the `<tr>`. If it fails (like our 403 authorization guard), show an alert with the error message and restore the button state."
**Result**: AI-generated. The script perfectly matched the error states (404, 403, 500) and smoothly removed the DOM node on success.

**Integrity Signature**: All AI output was reviewed to ensure the feedback messages were helpful, human-readable, and consistent across the application.
