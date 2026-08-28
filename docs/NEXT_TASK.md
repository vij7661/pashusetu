# PashuSetu — Current Agent Task

**Task ID:** `QA-FARMER-ADD-GOAT-001`

**Status:** `READY`

**Priority:** QA BLOCKER — highest priority. Stop unrelated work until resolved.

**Related defect:** GitHub #18 — `BLOCKER: Farmer Add Goat flow cannot continue after Individual Goat creation`.

## Objective

Reproduce and fix the current manual-QA blocker on Farmer Flutter Web `/#/livestock/new`: valid Individual Goat data can be entered, but the tester is unable to continue after the Add Individual Goat step.

## Required investigation

1. Start from the current approved branch and isolated QA environment. Preserve QA data safety.
2. Reproduce the exact Flutter Web path from an authenticated Farmer to Add Goat / Create Lot.
3. Inspect the Individual Goat submit button handler, repository/API call, loading/error state, response mapping and post-success navigation.
4. Capture sanitized evidence only: HTTP method/path, response status/domain code, whether a goat row was created, authenticated Farmer ownership, and returned persisted Goat ID. Do not expose sensitive identity/KYC/payout values.
5. Determine whether the UI is stuck before API submission, after successful API creation, or because an error is swallowed/poorly surfaced.
6. Check whether the Goat ID displayed before submission is only a generated display/client value and whether it conflicts with authoritative backend identity/state.
7. Fix the root cause with the smallest change. Do not weaken authentication, Farmer ownership, idempotency, auditability, or validation.

## Required behavior after fix

- Valid Individual Goat submission creates exactly one goat owned by the authenticated Farmer.
- The UI provides a friendly success state and navigates to the correct existing approved next Farmer state/route.
- The created goat can be retrieved from the backend and appears in Farmer livestock state.
- Rapid/double submit cannot create duplicate side effects.
- API/network/business failures remain on a recoverable screen with friendly localized messaging; no Dio exception, raw JSON, HTTP internals or stack trace is rendered.
- Existing Lot creation behavior must not regress.

## Mandatory automation / regression

Per `AGENTS.md`, pytest is a mandatory backend/API regression gate for applicable changes.

Run targeted tests first, add regression coverage for the defect, then run the full backend pytest suite before PASS. Also run Farmer Flutter repository/widget/navigation tests covering successful Individual Goat submission, failure handling, busy/double-click behavior and navigation. Run full Farmer `flutter test`, `flutter analyze`, and web build.

If backend/API behavior is involved, prove the persisted goat count/ownership and retrieval using pytest integration coverage. Do not report PASS with a failing test or by weakening/removing an assertion.

## Evidence handoff

Update `docs/AGENT_REPORT.md` with Task ID `QA-FARMER-ADD-GOAT-001` and status `PASS — CANDIDATE READY FOR QA REVIEW`, `BLOCKED`, or `FAILED`.

Report exact root cause, files changed, sanitized request/result evidence, exact Flutter and pytest counts, persisted exactly-one-goat evidence, known gaps, and a concise fresh-Chrome manual retest script.

A true browser human retest remains **MANUAL REQUIRED**. Do not close #18 automatically.

## Scope/safety

No Buyer/Admin implementation, payment/KYC provider changes, Bluetooth work, pilot/production mutation, deployment, merge to main, force-push, destructive Docker cleanup, or unrelated refactor.
