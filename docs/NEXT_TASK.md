# PashuSetu — Current Agent Task

**Task ID:** `PILOT-STABILIZATION-006`

**Status:** `READY`

**Work item:** Consolidated Golden-Path Stabilization — Farmer/Operator/Buyer end-to-end readiness gate

**Current objective:** Stabilize the complete controlled-pilot golden path already implemented across Farmer, Operator, Buyer and backend, close only confirmed integration/regression gaps, and produce a readiness verdict for human QA. Do not add new product features in this task.

## Requirements authority

Follow `/AGENTS.md`, the approved SRS/MVP behavior, and validated implementations from `PILOT-GOLDENPATH-001` through `PILOT-GOLDENPATH-005`.

## Golden path under test

Farmer registration/login → language/profile → goat/lot registration → Operator verification/weighment → Farmer acknowledgement/reweigh → listing creation → Buyer quantity-first search → nearest-first eligible inventory → whole-lot/valid partial-lot bid → idempotent multiple bids → exactly overlap-safe acceptance → authoritative agreement snapshot → pickup evidence → delivery evidence → trusted final weighment → 1.5% tolerance → settlement-ready OR dispute.

Also preserve the approved pilot rule that lot/competitive-bid purchases use minimum 3 goats. Do not invent a separate sub-3 commercial flow in this task unless such a flow is already explicitly present in the approved SRS/codebase; if the current UI suggests one but the backend does not support it, report the inconsistency rather than silently implementing a new business rule.

## Stabilization rules

- No new architecture, pricing, payment, KYC, logistics-provider, notification-provider or settlement features.
- Fix only confirmed defects that block or materially break the approved golden path.
- Preserve trust invariants: server-authoritative weights, idempotency, auditability, no double selling, immutable/versioned agreement, no transport estimate in commercial amount, 1.5% tolerance, no client timestamp priority.
- Do not weaken validation, authorization, concurrency, audit or evidence rules merely to make a test pass.
- GUI-only gaps that require human visual judgment may remain, but must be enumerated clearly.

## Execute autonomously

1. Follow AGENTS.md task-start sync and confirm working tree safety.
2. Verify Docker Compose, PostgreSQL, API, Alembic head and `/health`.
3. Run full baseline automated validation:
   - Farmer: `flutter pub get`, `flutter analyze`, `flutter test`
   - Buyer: `flutter pub get`, `flutter analyze`, `flutter test`
   - Operator: `flutter pub get`, `flutter analyze`, `flutter test`
   - Backend: focused lint on changed/critical files, targeted golden-path tests, then full `pytest`
4. Build or extend a synthetic consolidated regression that proves the principal backend/API state chain as far as practical without external services:
   - Farmer + livestock/lot creation
   - trusted weighment + acknowledgement
   - listing publication
   - Buyer discovery and valid bid
   - accepted Bid/Transaction
   - agreement snapshot
   - pickup/delivery evidence
   - final trusted weighment
   - one within-tolerance transaction → settlement-ready
   - one outside-tolerance transaction → dispute
5. Verify critical negative paths at minimum:
   - unverified livestock cannot list
   - unstable/untrusted reading cannot become authoritative
   - duplicate bid retry cannot duplicate commercial effect
   - overlapping selections cannot double-sell a goat
   - unauthorized/unrelated actors are rejected
   - transport estimate cannot alter agreement/transaction amount
   - locked agreement cannot be silently mutated
   - arbitrary client final weight cannot decide settlement
6. Inspect Farmer app end-to-end state/navigation contracts for registration, livestock/lot, weighment acknowledgement, listing, offer review/acceptance, agreement/transaction/status/dispute. Fix only confirmed integration/state/navigation blockers.
7. Inspect Buyer app end-to-end state/navigation contracts for auth, quantity/location search, nearest-first results, partial/whole-lot bid, transaction/agreement/status. Fix only confirmed blockers.
8. Inspect Operator app contracts for verification/weighment, pickup evidence, delivery/final weighment and transaction linkage. Fix only confirmed blockers.
9. Verify localization/state persistence for Farmer Telugu/English on screens touched by the golden path. Do not expand to unrelated localization polish.
10. Re-run every affected validation after fixes.
11. Inspect final diff, migration state, secret-pattern scan and generated-file noise; revert unrelated changes.
12. If all automated gates pass, commit and push the stabilization changes/report on the approved non-main branch.
13. Update `docs/AGENT_REPORT.md` with exact Task ID and one of these readiness outcomes:
   - `PASS — FARMER APP READY FOR QA`
   - `PASS — GOLDEN PATH READY FOR CONSOLIDATED QA`
   - `BLOCKED` with exact blocker
14. Include a concise human-QA checklist grouped by Farmer, Buyer, Operator, and transaction/dispute flow.
15. On PASS, do not invent another task automatically unless a different READY Task ID already exists.

## Farmer readiness gate

Codex may declare **`FARMER APP READY FOR QA`** only if all of the following are supported by actual checks:
- Farmer `flutter analyze` clean
- Farmer tests pass
- Farmer auth/registration backend contract proven
- goat and lot creation contract proven
- trusted weighment acknowledgement/reweigh contract proven
- listing creation and offer acceptance contract proven
- agreement/transaction/status/dispute Farmer-side contract has no known blocking integration error
- backend/API/PostgreSQL/migrations healthy
- no known architecture/business-rule ambiguity remains in the Farmer golden path
- remaining items are visual/manual QA or non-blocking polish, not structural rewrites

## Completion criteria

PASS requires the consolidated automated golden path and negative trust checks to succeed, all three Flutter apps to analyze/test cleanly where applicable, backend full suite to pass, local services/migrations to be healthy, no critical integration blocker to remain, and a precise QA handoff to be published.

## Completion report

Report exact readiness verdict; full test/analyze counts; consolidated API flow exercised; negative-path results; any fixes made; Farmer readiness-gate evaluation line by line; Buyer/Operator readiness notes; remaining manual QA checklist; branch/commit SHA(s); working tree state; and safety confirmation.
