# Queued Task — QA-AUTH-TESTDB-001

**Status:** `QUEUED`

**Work item:** Isolated QA/Test Database + OTP Test Provider + reusable synthetic pilot fixtures

## Objective

Create a safe, isolated local/QA testing data environment so Farmer, Buyer, Operator and Admin flows can be exercised repeatedly without using real phone numbers, real SMS, real personal data, Aadhaar, payment credentials, or production/pilot records.

This task must not weaken production authentication. All test-only behavior must be environment-gated and fail closed outside local/test/QA environments.

## Required design

### 1. Isolated test database

Use a separate PostgreSQL database/schema from normal local/pilot data, for example a dedicated `pashusetu_qa` database or equivalent clearly isolated test database selected by environment configuration.

Requirements:
- never point test reset/seed commands at production/pilot database URLs;
- destructive reset is permitted only against the explicitly identified QA/test database;
- normal development/pilot data must remain untouched;
- migrations must be applied to the QA database before seeding;
- provide one deterministic reset+seed command suitable for Codex and human QA.

### 2. Test-only OTP provider

Implement an OTP provider/adaptor dedicated to local/test/QA environments.

Requirements:
- do not send real SMS;
- do not call a paid provider;
- do not contact arbitrary real phone numbers;
- test identities must be explicitly allowlisted synthetic identities;
- OTP challenges must still exercise expiry, attempt count, one-time consumption, resend/rate-limit and verification state where those concepts exist in the approved auth design;
- OTP verification must remain server-authoritative;
- production/provider OTP code path must remain separate and unchanged except for the provider boundary needed to select the test adaptor;
- application startup/config must reject test OTP mode in production/pilot environment.

For automation, either:
- use a deterministic test OTP known only inside local/QA configuration, OR
- expose a local/test-only OTP inbox/readback mechanism that automated tests can query.

Whichever approach is used, it must be impossible to enable accidentally in production/pilot configuration.

### 3. Synthetic identities

Seed synthetic test accounts for at minimum:
- Farmer A — new/unverified onboarding case
- Farmer B — verified/profile-complete case
- Buyer A
- Buyer B
- Operator A
- Admin A

Use clearly synthetic names/identifiers and never seed real personal data. If the API currently requires phone-shaped strings, use values reserved strictly inside the test provider allowlist and ensure no real SMS can ever be sent to them.

### 4. Reusable business fixtures

Seed enough safe synthetic data to support repeatable QA of the existing golden path without manually recreating everything each run, while still allowing a clean new-user case.

Recommended fixture groups:
- empty/fresh Farmer onboarding state
- verified Farmer + 3+ individually identified goats with trusted per-goat weights
- whole-lot aggregate case where relevant
- active marketplace listing
- two Buyers capable of bidding
- accepted-transaction fixture only if it does not bypass the flow under test
- Operator assignment/centre fixture with trusted coordinates

Fixtures must be clearly named and documented so QA knows which account/state to use.

### 5. QA commands

Provide simple repository commands/scripts such as conceptually:
- `qa db reset`
- `qa db seed`
- `qa auth show otp <test identity>` or equivalent test-only readback
- `test farmer app --qa-data` / equivalent launcher integration where appropriate

Exact command names may differ, but human QA should not need to manually edit SQL or environment variables for ordinary test runs.

### 6. Automated coverage

Add tests proving at minimum:
- QA DB cannot accidentally resolve to the configured normal/pilot database;
- test OTP mode is rejected in production/pilot environment;
- allowlisted synthetic identity can request and verify OTP;
- unknown/non-test identity cannot use the test OTP bypass/provider;
- OTP expires;
- wrong OTP fails and attempt rules are enforced;
- OTP is single-use after successful verification;
- resend/retry behavior is deterministic;
- Farmer/Buyer/Operator role creation from verified synthetic OTP follows normal authorization rules;
- reset/seed produces deterministic fixture counts/identities.

## Security constraints

- No universal OTP bypass in shared production code.
- No hard-coded production secret or credential.
- No real phone numbers, Aadhaar, bank/UPI or payment information.
- Do not log OTPs in normal production-capable logs.
- Any test OTP readback endpoint/tool must be compiled/configured/guarded for local/test/QA only.
- Never weaken auth/authorization to simplify UI testing.

## Completion criteria

PASS requires a demonstrably isolated QA database, deterministic synthetic fixtures, a safe test-only OTP workflow, documented one-command reset/seed usage, automated negative/security tests, and proof that normal local/pilot/production auth/data paths remain unaffected.

## Scheduling note

This task is queued while `QA-FARMER-L10N-001` is active. Publish it into `docs/NEXT_TASK.md` only after the current localization defect task has completed, unless the human explicitly asks to interrupt the current task.
