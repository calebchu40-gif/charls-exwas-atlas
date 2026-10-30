# 2026-10-31 — Harden permissions for future private scan outputs

- The Wave 1 scale-up runner already constrained result paths to the private workspace. It now also sets the result directory to owner-only mode (0700) and each result, pair-QA, and manifest file to owner-only mode (0600), independent of the server's default umask.
- This applies only if a reviewed batch is later authorized; it does not open the analysis gate. No participant data or model was accessed in this change.
