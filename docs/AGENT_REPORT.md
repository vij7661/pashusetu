# PashuSetu — Agent Execution Report

- **Task ID:** `PILOT-GOLDENPATH-005`
- **Objective:** Accepted offer → authoritative agreement snapshot → attributable pickup/delivery evidence → trusted final weighment → tolerance → settlement-ready/dispute routing.
- **Timestamp:** 2026-08-27T16:30:10+05:30
- **Branch:** `feat/issue-4-local-backend-farmer-integration`
- **Status:** `PASS`

## Business/trust result

- Reused the repository-approved tolerance stored as `Agreement.tolerance_basis_points`: `150` basis points = `1.5%`. The API rejects agreement proposals with any other pilot tolerance.
- Agreement versions snapshot the accepted Bid ID, transaction/listing, Farmer and Buyer profiles, exact selected Goat IDs/whole-lot intent, accepted price/kg, trusted selection weight and livestock amount. The livestock amount is accepted price/kg × trusted selection weight, rounded to paise; transport estimates are absent.
- A `(transaction_id, version)` uniqueness constraint plus transaction row locking serializes agreement version creation. Locked agreement confirmation is an idempotent no-op; no mutation endpoint was introduced.
- Pickup and delivery records retain transaction, actor, server timestamps, synthetic local evidence reference and retry key. Audit events record pickup evidence and delivery/tolerance decisions.
- Pickup is restricted to the Operator who produced the listing's trusted origin weighment. Finalization is restricted to the active Operator who produced the referenced verified delivery weighment, with Farmer/listing target-scope checks.
- Tolerance compares the preserved accepted-selection weight with a separate locked final reading; the original weight/readings are not overwritten and arbitrary client final-weight values are not accepted.
- Within `1.5%` routes `TOLERANCE_CHECK → SETTLEMENT_READY`; outside routes to `DISPUTED` and creates/reuses one open dispute. No payment capture/movement was implemented.
- Transaction row locks, unique transaction evidence/dispute records and same-key replay responses prevent duplicate/contradictory effects. Different retry keys after evidence/finalization receive immutable-record conflicts.

## Migration and environment

- Non-destructive migration `0009_pilot_evidence` is current head. It adds agreement snapshot fields, evidence attribution/retry fields, preserved tolerance-decision values and agreement-version uniqueness; it drops/resets no data in upgrade.
- Docker Compose valid; PostgreSQL healthy; API running; `/health` HTTP `200`.

## Exact validation

- Focused Ruff on changed backend/migration/test files: `All checks passed!` with existing FastAPI `B008` and executable-bit `EXE002` exclusions.
- Focused transaction-evidence tests: `5 passed in 2.93s`.
- Full backend: `46 passed, 1 warning in 7.54s`. Warning is the existing Starlette/httpx TestClient deprecation.
- Farmer: `flutter pub get` passed; analyze `No issues found! (ran in 12.6s)`; `7 passed`.
- Buyer: `flutter pub get` passed; analyze `No issues found! (ran in 12.5s)`; `2 passed`.
- Operator: `flutter pub get` passed; analyze `No issues found! (ran in 10.1s)`; `2 passed`.
- `git diff --check`: passed. Alembic: `0009_pilot_evidence (head)`.

## Files and commits

- Agreement models/schemas/service/router; transaction state model; settlement eligibility.
- Logistics evidence models/schemas/service/router and append-only audit calls.
- Alembic migration `0009_pilot_transaction_evidence.py` and focused regression tests.
- Operator logistics repository and pickup/delivery verification screen.
- **Implementation commit:** `b9887567a714972fc4a9f8d366363f6ba3a70b10`
- **Proof/test commit:** `c4ac4fa3a15ea47e0aa2ec67677885d1449b4da9`
- Working tree: expected clean after this report commit.

## Known limitations / QA next action

- Automated coverage proves snapshot derivation, locked immutability, exact selection-weight use, tolerance boundary/state contracts and evidence command contracts; the full backend suite exercises existing PostgreSQL integration flows. A single synthetic HTTP script spanning every new endpoint was not added.
- Human QA should run one within-tolerance and one outside-tolerance transaction through the Operator screen, then inspect Buyer/Farmer status and Admin audit history. Synthetic evidence only; no real storage, booking or payment execution.
- Recommended next action: review commits and perform consolidated golden-path visual/API QA.

## Safety

No prohibited/destructive action occurred. No database/table/data/volume/container/image was deleted or reset; no destructive migration ran; no authorization/audit control was weakened. No secrets, credentials, raw Aadhaar/KYC/payment data or real personal data were used. No merge to `main`, force-push, production deployment, real payment action or paid external service action occurred.
