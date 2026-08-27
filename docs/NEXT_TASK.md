# PashuSetu — Current Agent Task

**Task ID:** `QA-FARMER-L10N-001`

**Status:** `READY`

**Work item:** Farmer QA defects — first-launch localization + mobile-number validation/autofill

**Current objective:** Fix the Farmer app onboarding/localization initialization defect found during manual Chrome QA and the mobile-number input defect found on the registration screen. On a fresh app/browser state, the user must not be forced directly into Telugu registration, and the mobile field must not auto-populate with stale/generated/debug values. The user must deliberately enter a valid 10-digit mobile number.

## QA evidence

Manual QA showed:
- the Farmer app opening at `#/register` in Telugu without a deliberate language-selection step;
- the mobile-number field behaving as though a prior/generated number could be reused/auto-populated;
- registration then surfacing a generic API error.

Treat these as onboarding/localization/input-validation defects. Do not change marketplace business rules.

## Important interactive-QA rule

- Do **not** repeatedly launch Chrome while diagnosing/fixing this task.
- Prefer automated widget/provider/router/input tests, `flutter analyze`, `flutter test`, and non-interactive web checks.
- At most **one** interactive Chrome launch is allowed at the end for a final smoke check unless the human explicitly asks for another launch.
- Reuse an existing Farmer web instance/hot reload where practical.
- Publish PASS/BLOCKED and stop; do not keep relaunching until full manual E2E QA is complete.

## Expected behavior

### Startup/localization
1. Fresh app state / cleared browser storage:
   - app opens the approved initial welcome/language-selection screen, not registration;
   - no language is silently forced in a way that bypasses the language-selection step.
2. Explicit English selection drives English onboarding and persists on refresh/relaunch.
3. Explicit Telugu selection drives Telugu onboarding and persists on refresh/relaunch.
4. Persisted locale must not bypass required onboarding/auth routing.

### Mobile-number input
5. Fresh registration must show an **empty** mobile-number field. Do not prefill real-looking, generated, debug, browser-restored or seeded phone values in normal QA startup.
6. Mobile input must contain **digits only** and represent exactly **10 digits** for this pilot UI contract.
7. More than 10 digits must never be accepted as a valid number. Prefer preventing entry beyond 10 digits at the field/input-formatter level; if an overlength value reaches validation by paste/browser autofill/programmatic state, show a clear localized **"Invalid mobile number"** error and do not call the OTP/API endpoint.
8. Fewer than 10 digits must also return the same invalid-mobile validation and must not call the OTP/API endpoint.
9. Non-digit characters, spaces, country-code prefixes typed into this field, and malformed values must be rejected/normalized only if the existing approved UX explicitly supports normalization. Do not silently turn arbitrary strings into a valid number.
10. Browser autofill/autocomplete must not inject an unrelated previously stored phone value into fresh QA registration where Flutter/web controls can prevent it.
11. Client-side validation is UX protection only; inspect the backend auth/OTP request contract and ensure the backend also rejects invalid mobile lengths/formats before creating OTP state. If the backend already validates correctly, do not redesign it.
12. A valid 10-digit test/QA number may proceed to the approved OTP flow/test provider once that environment is available.

## Authorized scope

Focused changes only in:
- Farmer Flutter startup/routing/localization/persistence;
- Farmer mobile-number form/input formatter/validation/autofill behavior;
- auth/OTP backend validation only if a confirmed gap exists;
- related focused tests;
- Farmer QA launcher only if stale browser state contributes to the defect.

## Execute autonomously

1. Follow `AGENTS.md` task-start sync and working-tree safety.
2. Diagnose the localization and phone-field defects primarily through code inspection and automated tests.
3. Inspect startup route, auth/onboarding guards, locale provider/storage, registration controllers, form initialization, browser autofill hints, input formatters and any debug/test seed values.
4. Identify root causes; do not merely force English or hard-code a test phone number.
5. Implement the smallest fixes preserving explicit locale selection/persistence and user-entered phone data.
6. Add/adjust automated tests covering at minimum:
   - fresh state begins at intended welcome/language entry;
   - English and Telugu selections work and persist;
   - persisted locale does not bypass onboarding;
   - fresh registration mobile field is empty;
   - 9-digit number rejected without API/OTP call;
   - 10-digit numeric number accepted by client validation;
   - 11+ digit number cannot be entered or is rejected without API/OTP call;
   - alphabetic/symbol malformed number rejected;
   - stale/debug/autofill phone seed is not populated in fresh QA state;
   - backend invalid-phone request rejection is tested if backend changes are required.
7. Run Farmer `flutter pub get`, `flutter analyze`, `flutter test`.
8. If backend changes occur, run targeted auth/OTP tests and full relevant backend suite.
9. Run a non-interactive web build/smoke check where practical. Only after automated checks pass may Codex perform one final interactive Chrome launch, and only if no Farmer QA instance is already running.
10. Inspect diff; avoid unrelated localization/input refactors.
11. Commit and push the focused fix on the approved non-main branch.
12. Update and push `docs/AGENT_REPORT.md` with this exact Task ID, root causes, files changed, exact test results, mobile-validation behavior and whether one human Chrome re-check is ready.
13. Stop after publishing PASS/BLOCKED.

## Completion criteria

PASS only when automated checks support corrected onboarding/localization initialization and the mobile field starts empty, accepts only a valid 10-digit number for the pilot UI contract, rejects malformed/short/overlength values without sending OTP/API requests, and the Farmer app is ready for one human re-check without repeated Chrome launches.
