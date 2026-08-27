# PashuSetu — Current Agent Task

**Task ID:** `QA-AUTH-TESTDB-001`

**Status:** `READY`

**Work item:** Build synchronized isolated QA database + canonical test fixtures for manual QA and automation

**Current objective:** Create an isolated QA/test data environment that is shared by manual QA and automation, with deterministic synthetic users, OTP behavior, livestock/lot/listing fixtures and safety guards that prevent any QA reset/seed/test-OTP operation from touching pilot/production data. Keep the canonical fixture identifiers and mobile numbers synchronized with the approved QA workbook.

## Canonical QA fixture contract

Use these fixture IDs and synthetic 10-digit local mobile numbers as the canonical seeded users. Prefixes are intentionally mixed; no role is tied to any prefix.

- `FARMER_EN_001` — Farmer — `6123456789` — English
- `FARMER_TE_001` — Farmer — `7234567890` — Telugu
- `FARMER_SUB3_001` — Farmer — `8345678901` — English — fewer-than-3-goats scenario
- `BUYER_001` — Buyer — `9456789012` — English
- `OPERATOR_001` — Operator — `6789012345` — English
- `ADMIN_001` — Admin — `7890123456` — English

The same fixture IDs/numbers must be used by manual QA instructions, seed scripts, backend/API tests and any Flutter/automation fixture references. Do not create a second conflicting user-number set.

## Mobile-number rules

- Local mobile input is exactly 10 digits.
- First digit must be one of `6`, `7`, `8`, `9`.
- Prefix is not role-specific; any role may use any valid prefix.
- `0`-`5` starting digits must be rejected as invalid for this pilot mobile contract.
- QA API boundary may convert validated local input to `+91<10 digits>` internally.
- Valid-but-unseeded 10-digit numbers in QA return `QA_TEST_USER_NOT_FOUND` (or equivalent clear QA response), create no OTP challenge and send no SMS.
- Invalid length/format/prefix is rejected before OTP state creation.

## QA database isolation

Create/use an explicitly isolated QA database, e.g. `pashusetu_qa`, or an equivalent existing test database if the repository already has a safe convention.

Hard safety requirements:
- QA seed/reset/cleanup commands must verify both environment identity and target DB identity before mutating data.
- Commands must fail closed if environment is not explicit LOCAL/QA/TEST or if DB identity is ambiguous/non-QA.
- Never reset/seed/drop/truncate pilot/production data.
- Do not share QA and pilot DB connection strings.
- No real phone numbers, Aadhaar, payment credentials or personal data.
- Test OTP provider must be disabled/fail closed outside isolated QA/test configuration.
- Do not integrate a real SMS provider in this task.

## Manual + automation shared data

Manual QA and automation should reference the same logical fixtures. Build a deterministic seeding mechanism so the environment can be recreated safely.

At minimum seed/provide:
- the six canonical users above;
- test OTP profiles for valid, wrong, expired, reuse and resend scenarios;
- livestock/goat/lot fixtures sufficient for Farmer manual QA and existing marketplace automation;
- a dedicated `FARMER_SUB3_001` data path for fewer-than-3-goats behavior without changing the approved minimum-3 Buyer competitive-lot purchase rule;
- verified and unverified livestock/listing states;
- enough Buyer/Operator/Admin linkage for later E2E QA;
- stable fixture IDs/codes rather than relying on random database-generated values in test instructions where practical.

Do not pre-populate the Farmer registration input field with these numbers. The workbook/fixtures are references for the tester; fresh UI fields remain empty.

## OTP QA behavior

The QA OTP provider must exercise real auth state behavior without real SMS:
- seeded QA user + valid request → deterministic/test-readable OTP challenge through approved QA mechanism;
- wrong OTP rejected and attempt behavior preserved;
- expired OTP rejected;
- verified OTP cannot be reused;
- resend invalidates/replaces prior OTP as defined by existing auth rules;
- unseeded valid mobile → QA user not found, zero challenge side effect;
- invalid mobile → validation rejection, zero challenge side effect.

Avoid one universal insecure production-style bypass. QA determinism must exist only behind explicit QA/test environment controls.

## Authorized scope

Focused changes allowed in:
- backend QA/test data/fixture/seeding support;
- Docker Compose or test-only environment wiring required to isolate QA DB safely;
- auth/OTP QA provider configuration and tests;
- non-destructive test-only migration/fixture support if required;
- reusable test fixture modules for backend/API/Flutter automation references;
- documentation mapping canonical fixture IDs to seeded data.

Do not implement new product features, real SMS, payments, KYC, Bluetooth, production deployment, or pilot DB mutations.

## Execute autonomously

1. Follow `AGENTS.md` task-start sync and working-tree safety.
2. Inspect current Docker/PostgreSQL/auth test setup and existing test fixtures before introducing another convention.
3. Design the smallest explicit QA DB isolation mechanism compatible with the repo.
4. Implement hard environment/DB identity safety guards before any reset/seed command.
5. Implement deterministic seed/upsert behavior for the canonical fixtures above. Re-running seed should not create duplicates or corrupt state.
6. Implement/align QA OTP behavior with seeded-vs-unseeded rules.
7. Add test coverage for all four valid prefixes `6/7/8/9`, invalid `0-5` prefixes, short/long/malformed numbers, seeded OTP success and unseeded zero-side-effect failure.
8. Add tests proving reset/seed/test-OTP commands refuse non-QA/pilot/production configuration.
9. Seed livestock/lot/listing/linkage fixtures needed for manual Farmer QA and later automation, including sub-3 Farmer data.
10. Provide one safe documented command/workflow to initialize/reset the QA DB and seed canonical data; do not require the human to type destructive raw SQL.
11. Run Docker config/health, migrations, targeted auth/fixture tests and full backend tests.
12. Ensure Farmer Flutter tests remain green if shared auth/test contracts changed.
13. Inspect diff, secret scan and safety guards.
14. Commit and push focused changes on the approved non-main branch.
15. Update `docs/AGENT_REPORT.md` with Task ID/status, exact DB/environment names, canonical seeded fixture mapping, OTP behavior, reset/seed command, safety proof, tests, commits and whether manual Farmer QA is ready to resume.
16. Stop after PASS/BLOCKED. Do not launch Chrome automatically as part of this task.

## Completion criteria

PASS requires an isolated reusable QA database/data workflow shared by manual QA and automation; canonical fixture IDs/numbers exactly match this task; 6/7/8/9 prefixes are accepted without role coupling; invalid prefixes/formats are rejected; seeded-only test OTP behavior works; unseeded valid mobiles create no OTP side effects; seed/reset is deterministic/idempotent and fails closed against non-QA targets; required Farmer/marketplace fixture data is available; backend validation is green; no pilot/production or real personal data is touched.
