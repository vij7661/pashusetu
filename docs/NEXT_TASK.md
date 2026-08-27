# PashuSetu — Current Agent Task

**Task ID:** `ISSUE-4-FARMER-INTEGRATION-002`

**Status:** `READY`

**Work item:** GitHub Issue #4 — Local PostgreSQL backend + Farmer integration

**Current objective:** Complete and validate the Farmer application's real local-backend integration so a test Farmer can authenticate/register through the running FastAPI/PostgreSQL stack and the client can reach its authenticated Home flow without connection/configuration failures.

## Context

The previous backend environment task passed:
- Docker Desktop Linux engine available
- Compose valid
- PostgreSQL healthy
- API running on port 8000
- Alembic upgrade passed
- `/health` HTTP 200
- backend suite: 36 passed, 1 existing warning

Do not spend this task on repository-wide Ruff cleanup; that is separate technical debt.

## Requirements authority

Follow `/AGENTS.md` and the approved SRS/MVP behavior. For this task, preserve the existing Farmer onboarding/business flow. Do not redesign KYC, payout, pricing, bidding, transaction, or other unrelated product behavior.

## Authorized scope

You MAY make focused changes required for Farmer-to-local-backend integration in:
- `apps/farmer_mobile`
- backend auth/Farmer profile endpoints only if a confirmed integration defect requires it
- local development documentation/config defaults where required
- focused automated tests for this integration

Do not merge to `main`.
Do not delete databases/volumes/data.
Do not introduce real Aadhaar/KYC/payment integrations or secrets.

## Execute autonomously

1. Pull/inspect the current branch and confirm Docker `db` and `api` remain healthy. If they are stopped, start the existing development services under the normal AGENTS.md rules.
2. In `apps/farmer_mobile`, run:
   - `flutter pub get`
   - `flutter analyze`
   - `flutter test`
3. Inspect Farmer API configuration and confirm development defaults are correct for at least:
   - Flutter Web/Chrome: `http://localhost:8000/api/v1`
   - Android emulator: `http://10.0.2.2:8000/api/v1`
   Preserve an override mechanism such as `--dart-define=API_BASE_URL=...` if already used.
4. Inspect the Farmer auth/onboarding repository code and backend auth/profile contracts. Trace the real path for:
   - mobile/OTP request
   - OTP verification/session token
   - Farmer registration/profile persistence
   - authenticated profile retrieval or equivalent session validation
   - transition/navigation to Farmer Home
5. Exercise the backend contract with safe development/test data through API/integration tests. Do not use real Aadhaar or personal data.
6. Determine whether the current Farmer client and backend contracts actually match. Fix only confirmed integration defects, using the smallest correct change. Common acceptable fixes include endpoint/path mismatch, request/response DTO mismatch, token handling, API base URL handling, CORS/local development behavior, or navigation after a successful registration response.
7. Preserve existing English/Telugu behavior. Do not broaden localization scope in this task.
8. Add or update focused automated tests so the corrected integration contract is regression-covered where practical.
9. Re-run:
   - Farmer `flutter analyze`
   - Farmer `flutter test`
   - relevant targeted backend tests
   - full backend pytest suite if backend code changes
   - `/health` check
10. Inspect the diff and remove unrelated/generated changes.
11. If all relevant checks pass, commit and push the validated focused integration changes on the current non-main branch with an appropriate message such as `fix(farmer): complete local backend registration integration`.
12. Update and push `docs/AGENT_REPORT.md` with this exact Task ID and final status.
13. If status is `PASS`, follow the automatic task handoff rule in `AGENTS.md`: pull once and execute a different READY Task ID if one has already been published.

## Completion criteria

This task is `PASS` only when all of the following are supported by actual checks/tests, not assumption:
- local PostgreSQL/API stack is healthy
- Farmer Flutter dependency resolution succeeds
- Farmer `flutter analyze` passes
- Farmer `flutter test` passes
- development API-base behavior is correct for web and Android emulator
- Farmer auth/registration request and response contracts match the backend
- a safe development/test Farmer registration/authenticated-profile path succeeds against the local backend (or an automated integration test proves the same contract)
- no connection timeout/configuration mismatch remains in the validated path
- no prohibited/destructive action was performed

If GUI-only final navigation cannot be fully automated, explicitly distinguish what was automatically proven from what still requires human QA. Do not claim visual/E2E QA passed without evidence.

## Completion report

Report:
- Task ID and final status
- Farmer analyze/test results
- DB/API/health status
- exact registration/auth contract exercised
- root cause(s) of any integration defect fixed
- files changed
- backend test results if applicable
- branch and implementation commit SHA
- remaining manual QA steps, if any
- working tree status
- safety confirmation
