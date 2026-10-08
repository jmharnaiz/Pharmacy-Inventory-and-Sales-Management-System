# Final Retrospective

## What went well?
*   **Structured Architecture:** Adopting a strict separation between Routes (validation/HTTP) and Controllers (database logic) early on made testing and debugging significantly easier.
*   **Consistent Error Handling:** Agreeing on a standard `{"status": 422, "error": "msg"}` shape across the entire team allowed the frontend views to seamlessly display errors without needing custom logic for every single form.
*   **AI as a Tool, Not a Crutch:** Forcing ourselves to write the core logic by hand in Phase 2 made us confident enough to catch the subtle XSS and SQL overflow bugs the AI generated during Phase 4.

## What didn't?
*   **Early CSS Scope Creep:** We spent a bit too much time manually tweaking the dashboard CSS to match the wireframes perfectly before the data was actually bound, which caused some crunch time in Week 7.
*   **Adversarial Testing:** We didn't anticipate the SQLite overflow vulnerability until the Week 10 adversarial session. We assumed Python's integer handling would protect us, but the database layer had strict limits.

## What we would change next time / Concrete Lessons
1.  **Test Boundaries Early:** We will write tests for massive integers and XSS payloads at the same time we write the "happy path" tests, rather than waiting for a formal QA phase.
2.  **Define Env Vars from Day 1:** We hardcoded `pharmacy.db` for too long. Setting up `.env` files at the very beginning of the project prevents scrambling during deployment.
3.  **Trust the Guard Clauses:** Putting all validation at the absolute top of the route execution (before touching *any* business logic) proved to be the most resilient way to protect the app.
