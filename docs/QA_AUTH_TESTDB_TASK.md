# PashuSetu — QA Auth/Test DB Task

**Task ID:** `QA-AUTH-TESTDB-001`

**Priority:** HIGH — QA stabilization

## Objective

Create one isolated QA/test database and deterministic fixture set used by both manual QA and automation. Keep it completely separated from pilot/production data. Synchronize fixture identifiers and mobile numbers with the manual QA workbook.

## Mobile-number contract

- Local UI mobile input is exactly 10 digits, digits only.
- The first digit must be one of `6`, `7`, `8`, or `9`.
- No prefix is tied to a role. Farmer, Buyer, Operator, and Admin fixtures may use any of 6/7/8/9.
- Values beginning with 0-5 are invalid for the pilot mobile-number contract and must be rejected before OTP state is created.
- Backend E.164 boundary should accept only `+91` followed by a valid local 10-digit number starting 6/7/8/9 for this pilot contract.

## Canonical QA fixtures

Use these exact synthetic local mobile numbers as the canonical starting fixture set unless an existing unique constraint requires a documented equivalent update:

- `FARMER_EN_001` → `6123456789`
- `FARMER_TE_001` → `7234567890`
- `FARMER_SUB3_001` → `8345678901`
- `BUYER_001` → `9456789012`
- `OPERATOR_001` → `6789012345`
- `ADMIN_001` → `7890123456`

Manual QA and automation must reference fixture IDs, not invent unrelated numbers.

## Required validation coverage

Prove all four valid starts are accepted by format validation:
- `6xxxxxxxxx`
- `7xxxxxxxxx`
- `8xxxxxxxxx`
- `9xxxxxxxxx`

Also prove rejection with no OTP/API side effect for:
- empty input
- 9 digits
- 11+ digits
- letters/symbols/spaces
- `+91` typed into the local-number field
- 10-digit values beginning 0,1,2,3,4,5

In isolated QA mode:
- seeded valid fixture → test OTP flow permitted;
- valid-format but unseeded number → `QA_TEST_USER_NOT_FOUND` (or approved localized equivalent), zero OTP challenge creation, no SMS;
- test OTP mode must fail closed outside explicitly isolated QA/test DB/environment.

## Data isolation

- Use a dedicated QA database/schema/connection, e.g. `pashusetu_qa` or equivalent explicit QA target.
- QA seed/reset/cleanup commands must positively verify QA environment/database identity before mutation.
- They must refuse to operate on pilot, production, or unknown DB targets.
- Never copy real/pilot user data into QA fixtures.
- All fixture names, phones, livestock, bids, transactions and OTPs are synthetic.

## Shared manual + automation data

The same fixture IDs/data are to support:
- manual Chrome QA;
- later Android/iOS QA where applicable;
- pytest/API regression;
- Flutter/widget/integration tests where deterministic fixtures are useful.

Do not maintain a second disconnected hard-coded test-phone list in source. Prefer one canonical seed definition/source that tests and QA setup consume.

## Completion proof

Report exact database/environment guard, seeded fixture IDs/numbers, OTP behavior, prefix validation tests for 6/7/8/9, invalid-prefix tests for 0-5, seeded-vs-unseeded behavior, manual/automation fixture synchronization, and confirmation that pilot/production data cannot be targeted by QA seed/reset commands.
