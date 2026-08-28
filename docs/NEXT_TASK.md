# PashuSetu — Current Agent Task

**Task ID:** `QA-FARMER-FINAL-SUBMIT-001`

**Status:** `READY`

**Priority:** QA BLOCKER — highest priority. Stop unrelated work until this is resolved.

**Related defect:** GitHub #16 — `BLOCKER: Farmer registration fails on final Review/Submit after KYC and payout`.

## Objective

Fix the real browser/UI failure where a valid new-Farmer registration reaches Review Registration with completed QA KYC + payout + consent, but **Submit Registration** returns a generic 4xx-style message and does not navigate to Home.

Do not rely on the previous backend-only `201` integration result as sufficient proof. Reproduce and validate the same path the human tester uses through the Flutter Web client against the isolated `pashusetu_qa` backend.

## Required investigation

1. Start from a clean, identity-guarded QA reset/seed.
2. Reproduce the full new-Farmer browser path with the canonical QA fixture.
3. Capture, in a sanitized developer report only:
   - final HTTP method + path;
   - sanitized request JSON shape/field names and non-sensitive values only;
   - HTTP status;
   - backend domain/error code;
   - relevant authoritative registration/profile state before and after submit.
4. Never print/log raw Aadhaar, full bank account, real/synthetic secret-like sensitive values beyond what is required in approved QA fixture docs. Use masked references.
5. Compare the actual Flutter repository/API serialization with the payload used by the previously successful backend integration test. Identify the exact mismatch rather than guessing.
6. Check whether reset/fixture lifecycle, a prior automated test, or a previous manual attempt already created the role-only Farmer profile and is causing conflict/duplicate behavior.
7. Inspect whether KYC status/provider reference, payout status/method/masked reference, language, profile fields, consent, and auth/user identity are all present in the shape expected by the final profile-completion contract.
8. Fix the root cause without weakening duplicate-profile protection, idempotency, auth/RBAC, QA isolation, or sensitive-data controls.

## Required behavior after fix

- Canonical QA new Farmer can complete: initial language -> mobile -> OTP -> Farmer Details/Location -> KYC -> Payout -> Review/Consent -> Submit -> Home.
- Final submit creates/completes exactly one Farmer profile for the authenticated role-only QA user.
- Repeated/double-click submit cannot create duplicate profiles or duplicate side effects.
- Successful final response contains only approved masked KYC/payout metadata; no raw Aadhaar/account data is persisted or returned.
- Existing Farmer login remains OTP -> Home and skips registration-only screens.
- User-facing failures remain friendly/localized; no raw Dio/backend codes/JSON/stack traces.

## Tests required

Add/adjust regression coverage that uses the same serialization path as the real Flutter wizard. At minimum:

- Flutter repository/controller test asserting exact final submit request shape (sanitized expected fields) and successful navigation/state;
- backend API/integration test for the exact UI payload;
- duplicate/repeat submit test proving exactly-one profile/business completion;
- existing-profile conflict test still rejects safely;
- KYC/payout masked-state assertions;
- full new-Farmer QA path after clean reset;
- existing Farmer shortcut remains green.

Where practical, add a non-interactive browser/E2E smoke that exercises the actual final submit boundary. If a true browser E2E cannot be made reliable in the current stack, state `MANUAL REQUIRED` and provide the exact reason; do not claim it passed.

## Validation gate

Run and report exact results for:
- guarded QA reset/seed (at least twice for deterministic state);
- migration status;
- API health;
- Farmer `flutter pub get`;
- Farmer `flutter analyze`;
- full Farmer `flutter test`;
- focused final-submit/repository tests;
- relevant backend registration/KYC/payout tests;
- full backend suite if backend changes;
- non-interactive web build;
- `git diff --check`;
- focused sensitive-data/logging scan.

## Evidence handoff

Update `docs/AGENT_REPORT.md` with Task ID `QA-FARMER-FINAL-SUBMIT-001` and either `CANDIDATE READY FOR QA REVIEW` or `BLOCKED`.

The report must include:
- exact root cause of issue #16;
- actual sanitized browser/UI request vs expected/successful test request comparison;
- files/commit changed;
- exact automated test counts;
- proof of one-and-only-one profile completion;
- known gaps/manual-required items;
- a concise manual retest script beginning from a clean QA reset and ending at Home.

Do not close GitHub #16 automatically. Human/independent QA closes it only after manual retest passes.

## Scope/safety

No real UIDAI integration, real Aadhaar, real bank/UPI, payments, Bluetooth, pilot/production DB mutation, deployment, merge to main, force-push, destructive Docker cleanup, or unrelated marketplace work.

Follow `AGENTS.md` sync/working-tree safety, commit/push the focused fix, publish the evidence report, then stop for independent QA review.
