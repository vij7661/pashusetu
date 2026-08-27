# PashuSetu — Current Agent Task

**Task ID:** `QA-FARMER-MANUAL-GATE-001`

**Status:** `READY`

**Priority:** QA BLOCKER — highest priority until Farmer manual-QA gate passes.

**Work item:** Farmer pre-manual-QA hardening + evidence handoff for independent QA review

## Objective

Act as implementation engineer and automated tester. Do not self-certify the Farmer app as human-QA-ready without evidence. Fix the known OTP exception-leak defect, review the implemented Farmer golden path for baseline defects, execute automated checks, and then publish a structured evidence package in GitHub that ChatGPT can independently read as the manual-QA reviewer.

The final readiness decision belongs to the independent reviewer after reading the evidence. Your report may state `CANDIDATE READY FOR QA REVIEW` only when your checks are green; do not state final human/manual-QA approval.

## Known blocker

Wrong OTP currently exposes raw technical text such as `DioException [bad response]` / `OTP_INVALID`. Expected auth failures must render localized user-friendly messages. Never expose Dio/HTTP/stack trace/backend class/raw JSON to normal users. Cover wrong, expired, reused, resend/rate-limit if present, offline/timeout, 4xx/5xx/unknown and correct QA OTP `4816`.

## Baseline review

Review implemented Farmer screens/contracts in the MVP golden path: language/onboarding, registration/mobile/OTP, Farmer details/profile, goat/lot forms, acknowledgement/listing and existing offer/agreement/status surfaces. Do not invent missing product features.

For each applicable critical action check: required/empty/null; type/format; min/max/boundary; trimming/paste; positive path; negative/business path; friendly localized error mapping; duplicate/repeated submit; loading state; back/refresh/recreation; English/Telugu; auth/session/ownership; UI/API data integrity; no fixture autofill into fresh forms; no technical exception leakage.

Specific required boundaries include mobile blank/9/10/11 digits, 6/7/8/9 valid prefixes, 0-5 invalid prefix, letters/symbols, seeded vs unseeded QA user; OTP blank/malformed/wrong/correct/expired/reused/resend/repeated submit/network/server failure; language fresh/English/Telugu/persistence/refresh; and below/exact/above boundaries for existing numeric/count business rules in implemented Farmer forms.

## Evidence package required for ChatGPT review

Update `docs/AGENT_REPORT.md` with Task ID and `CANDIDATE READY FOR QA REVIEW` or `BLOCKED`. The report must be specific enough for an independent QA reviewer to challenge the result, and must include:

1. **Requirements traceability matrix** — each implemented Farmer screen/action reviewed, relevant MVP/SRS/business rule, positive test, negative/boundary tests, result, and automated test name/file where applicable.
2. **Defect ledger** — every defect discovered in this gate, severity, root cause, fix, regression test, commit.
3. **Error-message matrix** — backend/domain condition/code -> English user message -> Telugu user message -> expected navigation/state. Explicitly prove raw exception text is absent.
4. **API/side-effect evidence** for critical negative cases — e.g. invalid mobile/unseeded QA number creates zero OTP challenge; wrong OTP does not authenticate/navigate; duplicate submit does not duplicate state where protected.
5. **State/navigation matrix** — fresh launch, language switch, refresh/recreate, back, failed auth, successful auth, and what state is expected/preserved.
6. **Exact command/test results** — flutter analyze, full flutter test, relevant backend tests/full suite if changed, web build/smoke, QA DB/API health. Give exact pass/fail counts, not just 'green'.
7. **Files/commits changed** and branch SHA.
8. **Known gaps / not tested** — explicitly list anything not actually proven. Never mark an untested item as pass.
9. **Manual test script for reviewer/human** — concise numbered steps using canonical QA fixture(s), expected result at every step, including at least one negative OTP case and one successful OTP case. Do not launch Chrome repeatedly while implementing.
10. **Screenshots/log artifacts if the repo workflow can safely produce them**; otherwise state why they are absent. Do not fabricate visual evidence.

If evidence exposes another basic defect, fix it and rerun before publishing candidate-ready status. If something cannot be verified automatically, mark it `MANUAL REQUIRED`, not PASS.

## Automated validation

Run Farmer `flutter pub get`, `flutter analyze`, full `flutter test`, relevant backend auth/Farmer tests, full backend suite if backend changes, non-interactive web build/smoke where practical, and isolated QA DB/API health as needed. Add regression tests for confirmed defects.

## Scope/safety

Focused Farmer UX/validation/error mapping/localization/tests and confirmed backend contract fixes only. No new marketplace features, real SMS, Aadhaar/KYC integration, payments, Bluetooth, production/pilot deployment, pilot DB mutation, unrelated refactor, or invented business rules. Preserve isolated QA OTP/database safeguards.

Follow `AGENTS.md` sync and working-tree safety. Commit/push focused changes. Stop after `CANDIDATE READY FOR QA REVIEW` or `BLOCKED` so ChatGPT can read `docs/AGENT_REPORT.md` and independently decide what happens next.
