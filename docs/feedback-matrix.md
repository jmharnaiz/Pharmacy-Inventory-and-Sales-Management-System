# Feedback Matrix

| Action | Loading | Success | Error |
|---|---|---|---|
| **Create Medicine** | "Save Medicine" button disabled + spinning icon | Redirects to List view | 422: Inline field errors (e.g., "Must be a positive number"). 500: Top red banner. |
| **Update Medicine** | "Update Medicine" button disabled + spinning icon | Redirects to List view | 422: Inline field errors. 500/Network: Top red banner. |
| **Delete Medicine** | Native confirmation prompt -> row fades out | Row disappears from table | 403: "Not allowed, admin only" alert. 500: General error alert. |
| **Load List** | Server-side rendered (Instant) / UI Skeleton if JS fetched | Table populates with records | 404/Empty: "No medicines found" illustration shown. |
