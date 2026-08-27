# PashuSetu — Current Agent Task

**Task ID:** `ISSUE-4-BACKEND-STATUS-001`

**Status:** `READY`

**Work item:** GitHub Issue #4 — Local PostgreSQL backend + Farmer integration

**Current objective:** Diagnose and fix the failing backend module status-route test, then rerun the full backend validation.

## Instructions

Follow all rules in `/AGENTS.md`.

This task AUTHORIZES a focused backend/test fix for the `_status` route contract failure.
Do not change business rules, transaction semantics, pricing, bidding, KYC, payments, or unrelated modules.
Do not delete containers, images, databases, Docker volumes, or data.
Do not change BIOS, WSL, Windows, or Docker Desktop system configuration.

## Known failure

`tests/test_api_modules.py::test_module_scaffolds_are_exposed` fails because `/api/v1/livestock/_status` returns HTTP 404 while the test expects HTTP 200 and JSON status `scaffolded`.

The current test loops across:
- livestock
- weighment
- marketplace
- bidding
- agreement
- transaction
- logistics
- payments
- disputes
- notifications
- audit

## Execute autonomously

1. Inspect `backend/tests/test_api_modules.py`, `backend/app/api.py`, and the routers for the listed modules.
2. Determine whether the failing test is stale because modules have progressed beyond scaffold status, or whether the API accidentally lost an intended compatibility/status route.
3. Choose the smallest correct fix based on the current codebase and repository documentation. Do not blindly add dead `_status` endpoints if the test is obsolete; do not weaken a valid contract merely to make a test green.
4. Implement only the focused fix needed for this contract/test mismatch.
5. Run the targeted failing test first.
6. Run the full backend test suite.
7. Run backend lint/static checks used by the repository if available.
8. Inspect the diff and exclude unrelated/generated changes.
9. If all relevant checks pass, commit and push the focused fix to the current non-main branch with an appropriate `fix(backend): ...` or `test(backend): ...` commit message.
10. Do not merge to `main`.
11. Update and push `docs/AGENT_REPORT.md` with this exact Task ID and final status.
12. If status is `PASS`, follow the Automatic task handoff section in `AGENTS.md`: pull once, re-read `docs/NEXT_TASK.md`, and automatically execute it only if a different Task ID is already published with `Status: READY`.

## Completion report

Report:
- Task ID
- root cause
- files changed
- targeted test result
- full backend test result
- lint/static-check result
- branch and commit SHA if committed
- any remaining blocker
- confirmation that no prohibited actions were performed

Do not claim Issue #4 is complete unless the backend runtime, migrations, health endpoint, and full backend tests all pass.
