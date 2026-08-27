# PashuSetu — Current Agent Task

**Task ID:** `QA-FARMER-MANUAL-GATE-001`

**Status:** `READY`

**Priority:** QA BLOCKER — highest priority until Farmer manual-QA gate passes.

**Work item:** Farmer pre-manual-QA hardening gate — OTP UX + baseline negative/boundary/error review

## Objective

Do not add new product features. Close the known OTP exception-leak defect and perform a focused pre-manual-QA baseline review of the Farmer onboarding/auth/profile/form flows so basic validation/error-state defects are caught automatically before the human resumes manual QA.

The app may be declared **`PASS — FARMER APP READY FOR MANUAL QA`** only after the gate below is supported by actual automated checks and code inspection. Otherwise publish `BLOCKED` with exact defects.

## Known blocker to fix first

Wrong OTP currently exposes raw technical text such as `DioException [bad response]` and `OTP_INVALID` in the UI. Replace expected auth failures with localized user-friendly messages while preserving backend error codes internally/debug-only.

At minimum handle:
- wrong OTP;
- expired OTP;
- reused/already-used OTP;
- resend/rate-limit state if present;
- offline/network timeout;
- backend 4xx/5xx/unknown response;
- correct QA OTP `4816` success.

No raw Dio/HTTP/stack trace/backend exception class/raw JSON may be displayed to a normal user.

## Baseline Farmer readiness checklist

Review the Farmer screens/contracts currently in the MVP golden path, prioritizing onboarding, language selection, registration/mobile/OTP, Farmer details/profile, goat/lot creation forms, acknowledgement/listing forms, and offer/agreement/status surfaces already implemented. Do not invent missing product features.

For each touched/critical form or action verify as applicable:

1. **Input contracts** — required/empty/null, allowed characters, min/max length/range, trimming, numeric bounds, paste/autofill, exact boundary values.
2. **Positive path** — valid input performs the intended action once, persists the correct value/state and navigates correctly.
3. **Negative/business path** — invalid input/business state is blocked with a clear localized message and no unintended API/business side effect.
4. **Error mapping** — known backend/domain codes map to localized friendly UI text; unexpected/network/server failures use a safe generic localized message; no technical exception leakage.
5. **Repeated actions** — double tap/click, retry and duplicate submission do not create duplicate commercial or auth effects; buttons/loading state are sensible where implemented.
6. **Navigation/state** — back/refresh/recreation does not incorrectly skip required onboarding, leak stale QA values, change locale, or corrupt in-progress state.
7. **Localization** — English and Telugu strings exist for critical validation/error messages touched by this gate.
8. **Auth/session safety** — invalid/expired auth does not navigate forward; successful auth preserves expected role/session behavior; QA OTP/test mode remains isolated.
9. **Role/ownership** — existing Farmer-side protected API calls remain authorized correctly; do not weaken backend authorization.
10. **Data integrity** — UI/API values agree for the fields covered; no debug/generated fixture data is injected into fresh forms.

## Specific boundary checks required now

- Mobile: blank, 9 digits, valid 10 digits starting 6/7/8/9, 11 digits/paste, letters/symbols, invalid 0-5 prefix, seeded vs valid-unseeded QA number.
- OTP: blank/malformed length if applicable, wrong, correct, expired, reused, resend, repeated submit, network/server failure.
- Language/onboarding: fresh state, English, Telugu, persisted locale, refresh/recreate, locale must not bypass auth/onboarding.
- Any numeric/count field in existing Farmer goat/lot/listing forms: below minimum / exact minimum / above minimum or max where a rule already exists in SRS/code. Do not invent a new threshold.
- Required text/select fields in existing Farmer forms: empty and valid cases.

## Automated coverage expectation

Add regression tests for any confirmed defect and enough widget/unit/repository tests to prove the baseline checks above for critical Farmer paths. A defect fixed during this task should normally receive an automated regression test.

Run:
- Farmer `flutter pub get`
- Farmer `flutter analyze`
- Farmer full `flutter test`
- relevant backend auth/Farmer tests
- full backend suite if backend source changes
- non-interactive web build/smoke check where practical
- isolated QA DB/API health checks as needed

Do not repeatedly launch Chrome during implementation. At most one final interactive launch is allowed only after all automated checks pass and only if no Farmer session is already running.

## Scope discipline

Allowed: focused Farmer UX/validation/error mapping/localization/tests and backend contract fixes only where a confirmed mismatch exists.

Not allowed: new marketplace features, real SMS, KYC/Aadhaar integration, payments, Bluetooth/device work, production/pilot deployment, pilot DB mutation, unrelated refactors, or business-rule invention.

## Completion report

Update `docs/AGENT_REPORT.md` with this exact Task ID and include:
- exact readiness verdict: `PASS — FARMER APP READY FOR MANUAL QA` or `BLOCKED`;
- defects found/fixed;
- checklist areas actually reviewed;
- exact test/analyze/build results;
- known untested/manual-only items;
- branch/commit SHA;
- QA DB/API health and safety confirmation.

## Completion criteria

PASS only when the known OTP exception leak is fixed; critical Farmer onboarding/auth/form validation and error handling have been reviewed against the baseline above; automated regression is green; no known basic blocker remains in the reviewed Farmer golden path; and remaining work is genuinely human visual/usability QA rather than missing elementary validation/error handling.
