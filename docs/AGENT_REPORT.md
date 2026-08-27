# PashuSetu — Agent Execution Report

- **Task ID:** `QA-AUTH-TESTDB-001`
- **Objective:** Provide a synchronized, deterministic, isolated QA database and canonical synthetic fixtures for manual QA and automation, with fail-closed OTP/reset safety.
- **Timestamp:** 2026-08-27T18:38:07+05:30
- **Branch:** `feat/issue-4-local-backend-farmer-integration`
- **Status:** `PASS`

## Environment and isolation

- QA environment: `APP_ENV=qa`.
- QA Compose service/database: `db_qa` / `pashusetu_qa`, exposed locally on port `5434`, with its own `pashusetu_qa_pg` volume.
- The API now uses the QA connection only in this local Compose QA workflow. The existing `db` service/database `pashusetu` remains separate and was not reset or seeded; final inspection showed its existing 2 users unchanged by the QA workflow.
- Reset/seed verifies all of: exact `APP_ENV=qa`, `DATABASE_ISOLATED_FOR_QA=true`, `OTP_TEST_MODE=true`, configured database name `pashusetu_qa`, and live PostgreSQL `current_database()=pashusetu_qa` before truncating fixture tables.
- OTP test configuration validation accepts only explicit local/QA/test environments with named `pashusetu_qa` or `pashusetu_test` databases and rejects pilot/production/normal database targets.

## Canonical fixture mapping

| Fixture | Role | Local mobile | Language |
| --- | --- | --- | --- |
| `FARMER_EN_001` | Farmer | `6123456789` | English |
| `FARMER_TE_001` | Farmer | `7234567890` | Telugu |
| `FARMER_SUB3_001` | Farmer | `8345678901` | English |
| `BUYER_001` | Buyer | `9456789012` | English |
| `OPERATOR_001` | Operator | `6789012345` | English |
| `ADMIN_001` | Admin | `7890123456` | English |

- Stable data includes verified/unverified goats, a verified 3-goat lot, a dedicated 2-goat/sub-3 draft lot, centre/operator/scale linkage, acknowledged weighment, and live listing `QA-LISTING-LIVE-001`.
- Final canonical counts after reset: 6 users, 3 Farmer profiles, 1 Buyer profile, 6 goats, 2 lots, and 1 listing.
- Manual instructions and automation import/reference the same fixture contract in `backend/app/db/qa_fixtures.py`; fresh Flutter fields remain empty.

## OTP and mobile behavior

- Local mobile input and backend E.164 validation accept exactly 10 digits beginning with `6`, `7`, `8`, or `9`; prefixes `0`–`5`, malformed, short, long, spaced, and local-field `+91` input are rejected.
- Seeded canonical users may receive the deterministic QA-only OTP `4816`; no real SMS/provider is used.
- Valid unseeded numbers return `QA_TEST_USER_NOT_FOUND` and create zero OTP challenges.
- Resend consumes/replaces earlier active challenges. Tests cover wrong OTP attempt handling, expiry, successful verification, normal role-bearing token issuance, single-use rejection, and resend behavior.

## Safe workflow

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\reset_qa_db.ps1
```

This starts only `db_qa`, migrates it, then performs the identity-guarded reset and deterministic seed. Running it twice produced the same fixture counts. `tools/start_farmer_qa.ps1` now invokes this workflow before starting the API; Chrome was not launched during this task.

## Exact validation

- `docker compose config --quiet`: passed.
- Guarded reset/migrate/seed: passed three times; repeat count output remained `{'users': 6, 'farmers': 3, 'buyers': 1, 'goats': 6, 'lots': 2, 'listings': 1}`.
- Focused QA/auth/fixture tests: `20 passed`, one upstream Starlette/httpx deprecation warning, in `4.70s`.
- Final full backend suite against `pashusetu_qa`: `67 passed`, one upstream Starlette/httpx deprecation warning, in `8.60s`.
- Focused Ruff on touched backend/QA files with repository-existing `EXE002`, `B008`, and `UP017` categories ignored: `All checks passed!`.
- Farmer `flutter pub get`: passed; informational newer incompatible package notices only.
- Farmer `flutter analyze`: `No issues found! (ran in 7.7s)`.
- Farmer `flutter test`: `15 passed`.
- API health after final reseed: HTTP 200, environment `qa`.
- `git diff --check`: passed; focused secret/private-key pattern scan found no matches.

## Files and commit

- Added canonical fixture definitions, guarded seed/reset implementation, OTP lifecycle/safety/fixture tests, QA fixture documentation, and the one-command PowerShell workflow.
- Updated Compose isolation, Farmer launcher wiring, auth mobile prefix validation, OTP resend behavior, configuration safeguards, and Farmer mobile tests.
- **Implementation commit:** `a59e4cec1546929991bfbb66ccc25a3a0933c465`
- Working tree: expected clean after the report commit.

## QA handoff

- Manual Farmer QA is ready to resume using `tools/start_farmer_qa.ps1` and the canonical numbers above.
- Known limitation: Chrome and Android were not launched in this database task; this establishes backend/data and automated Flutter confidence, not Android pilot readiness.

## Safety

No prohibited action occurred. The authorized destructive reset ran only after positive identity checks against the new isolated `pashusetu_qa` database. No pilot/production database, existing `pashusetu` database, real phone, real SMS, Aadhaar, payment credential, secret, production deployment, merge to `main`, force-push, Docker-volume deletion, or system configuration change was used or modified.
