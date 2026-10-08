# AI Prompt Log (Week 9)

*AI use is ON. Focus is on reviewing AI output.*

**AI Assistant Used**: Antigravity (Gemini)

## 1. Generating the AI-Assisted PR
**Prompt**: "Generate a simple Flask route to add a Category, but intentionally include 3-4 subtle bugs related to Python dictionary access, REST status codes, and error response shapes that contradict our Phase 2 guidelines."
**Result**: The AI generated a snippet that looked convincing but returned a 200 instead of 201, used a 400 instead of 422, formatted the JSON wrong, and included a dictionary `KeyError` trap. This was used as the payload for our "Find the Flaw" exercise.

**Integrity Signature**: We successfully subjected the AI output to our peer-review checklist (Correctness, Readability, Consistency, Security, Tests). All planted bugs were caught during the review process, enforcing the rule: *no red tests, no un-reviewed merges.*
