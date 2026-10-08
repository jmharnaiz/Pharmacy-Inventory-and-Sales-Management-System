# AI Prompt Log (Week 7)

*AI use is ON and required for this phase.*

**AI Assistant Used**: Antigravity (Gemini)

## 1. Scaffolding Fetch & Async Logic
**Prompt**: "Write the JavaScript `fetch` logic for the medicine form. It needs to handle both POST (create) and PUT (edit) depending on a data-mode attribute. Prevent default submission. It must disable the button and show a spinner class during the request. On 201/200, redirect to `/ui/medicines`. On 422, extract the `field` and `error` from our standard JSON response and display it in the corresponding `<span id="error-fieldname">`. On 500 or network failure, show it in the `#generalError` banner."
**Result**: AI-generated. The AI produced a robust `async/await` block. 
**Modifications**: Hand-modified. I realized that the HTML inputs for numbers were sending as strings in the JSON body, which failed our Python backend validation (which checks `type(val) in [int, float]`). I manually added type conversion (`parseFloat` and `parseInt`) to the JavaScript before stringifying the payload.

**Integrity Signature**: All AI output was reviewed and tested end-to-end to ensure the lifecycle behaves correctly without refreshing the page.
