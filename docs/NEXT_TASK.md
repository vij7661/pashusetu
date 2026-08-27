# PashuSetu — Current Agent Task

**Task ID:** `PILOT-GOLDENPATH-003`

**Status:** `READY`

**Work item:** Pilot Golden Path — Goat/Lot registration + Operator verification + Farmer acknowledgement

**Current objective:** Complete and validate the next pilot slice from authenticated Farmer livestock creation through Operator verification/weighment and Farmer acknowledgement, using the existing local FastAPI/PostgreSQL stack and simulated/adapted hardware where real Bluetooth/printing hardware is not yet integrated.

## Requirements authority

Follow `/AGENTS.md` and the approved SRS/MVP behavior. Preserve these trust rules:
- Farmer can create an individual goat or multi-goat lot.
- Listing weight must come from the Mandal Centre verification flow, not Farmer-entered weight.
- Operator must use registered Centre/Scale context and only lock a stable reading.
- Locked weighment must preserve gross/tare/net, Scale ID, Operator ID, Centre ID and authoritative server time.
- Farmer Rejects → fresh controlled reweigh/new weighment history.
- Farmer Accepts → acknowledgement/receipt path.
- There must be no normal acknowledgement → same weighing loop.
- Reweigh/corrections must not overwrite acknowledged/locked weighment history.

Do not redesign pricing, bidding, payments, KYC, settlement, disputes or unrelated architecture in this task.

## Authorized scope

You MAY make focused changes required for this slice in:
- `apps/farmer_mobile` livestock/weighment acknowledgement flows
- `apps/operator_mobile` verification/weighment flows
- backend livestock/weighment/identity/operator/centre/scale endpoints and schemas only where a confirmed integration defect requires it
- test fixtures/synthetic local development data required to exercise the flow
- focused automated tests and local development docs/config

Use simulator/adapter behavior for Bluetooth scale and receipt/print where current repository design already provides it. Do not introduce a real hardware vendor dependency in this task.

Do not merge to `main`.
Do not delete databases/volumes/existing data.
Do not use real Aadhaar/KYC/payment/personal data.

## Execute autonomously

1. Pull/inspect the current branch and verify Docker `db` and `api` are healthy; start existing dev services if needed under AGENTS.md.
2. Run baseline validation for affected Flutter apps:
   - Farmer: `flutter pub get`, `flutter analyze`, `flutter test`
   - Operator: `flutter pub get`, `flutter analyze`, `flutter test`
   Resolve only confirmed compatibility/dependency issues required to make the affected app testable.
3. Inspect current backend routes/models/services/tests for livestock and weighment plus Farmer/Operator client repositories/screens.
4. Using safe synthetic development data, prove or implement the authenticated Farmer path for:
   - create individual goat
   - create multi-goat lot
   - retrieve created livestock/lot as required by the client
5. Prove or implement the Operator verification path for a selected goat/lot:
   - authenticated/valid Operator + Centre context
   - registered Scale ID and valid calibration/status checks as currently modeled
   - capture/ingest simulated stable scale reading
   - prevent lock of unstable reading
   - lock weighment and preserve trusted fields
   - attach/reference verification evidence using the existing development mechanism
6. Prove or implement Farmer decision behavior against the verified record:
   - Reject creates/routes to a fresh weighment/reweigh path and preserves original history
   - Accept creates Farmer acknowledgement and receipt/QR record/payload if supported by current backend
   - completed acknowledgement does not route back to the same weighing action
7. Fix only confirmed API/DTO/state/navigation defects that block this approved flow. Do not weaken authorization, evidence, calibration, state, or history rules just to pass a test.
8. Add focused regression coverage for the core trust invariants, including at minimum:
   - individual goat and lot creation contracts
   - unstable reading cannot be locked
   - accepted/locked weighment fields persist correctly
   - rejection/reweigh preserves the previous weighment
   - acceptance/acknowledgement follows the correct branch
9. Exercise the live local API contract end-to-end as far as practical with synthetic data, in addition to unit/integration tests.
10. Re-run all relevant validation:
   - Farmer analyze/tests if changed
   - Operator analyze/tests if changed
   - targeted backend tests
   - full backend pytest suite if backend code changed
   - `/health`
11. Inspect the final diff and remove unrelated/generated changes.
12. If all relevant checks pass, commit and push the focused implementation on the approved non-main branch with appropriate focused commit message(s).
13. Update and push `docs/AGENT_REPORT.md` with this exact Task ID and final status.
14. If status is `PASS`, follow AGENTS.md automatic task handoff: pull once and execute a different READY Task ID if already published.

## Completion criteria

This task is `PASS` only when actual checks/tests support:
- Farmer can create individual goat and lot through the backend contract
- Operator verification can target that livestock/lot
- trusted scale/centre/operator checks are enforced according to current approved model
- unstable reading is not lockable
- stable verified reading can be locked with trusted fields/evidence reference
- Farmer Reject creates a fresh reweigh path without overwriting original history
- Farmer Accept creates acknowledgement and receipt/QR representation where supported
- no normal acknowledgement-to-same-weighment loop exists
- affected Flutter analyze/tests pass
- relevant backend tests pass and local API health remains good
- no prohibited/destructive action occurred

GUI-only visual behavior may remain for consolidated human QA later; clearly distinguish automated proof from pending visual QA.

## Completion report

Report:
- Task ID and final status
- root cause(s)/gaps found
- Farmer test/analyze results
- Operator test/analyze results
- exact live/API flow exercised
- trust-invariant test results
- backend targeted/full-suite results
- files changed
- branch and implementation commit SHA(s)
- remaining manual QA items
- working tree state
- safety confirmation
