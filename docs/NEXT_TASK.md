# PashuSetu — Current Agent Task

**Task ID:** `QA-FARMER-L10N-001`

**Status:** `READY`

**Work item:** Farmer QA defect — first launch incorrectly opens registration in Telugu

**Current objective:** Fix the Farmer app onboarding/localization initialization defect found during manual Chrome QA. On a fresh app/browser state, the user must not be forced directly into Telugu registration. The app must present the intended welcome/language-selection entry flow first, apply the language only after the user deliberately selects it, and persist that selection for later launches.

## QA evidence

Manual QA screenshot showed the Farmer app opening directly at `#/register` with Telugu strings and a prefilled phone number, without a deliberate language-selection step in the current QA session. Treat this as a localization/onboarding state defect. Do not change backend business rules.

## Important interactive-QA rule

- Do **not** repeatedly launch Chrome while diagnosing/fixing this task.
- During implementation, prefer automated widget/provider/router tests, `flutter analyze`, `flutter test`, and non-interactive/web build checks.
- At most **one** interactive Chrome launch is allowed at the end of the task for a final smoke check, unless the human explicitly asks for another launch.
- If a Farmer Flutter web instance is already running, reuse it/hot-reload where practical rather than starting another `flutter run` process or opening another Chrome instance.
- After automated validation passes, publish the report and stop. Human manual QA continues separately; Codex must not keep relaunching Chrome until the entire end-to-end scenario is manually completed.

## Expected behavior

1. Fresh app state / cleared browser storage:
   - app opens the approved initial welcome/language-selection screen, not registration;
   - no language is silently forced by stale/default state in a way that bypasses the language-selection step.
2. User explicitly selects English:
   - registration/login/onboarding displays English;
   - language persists on refresh/relaunch unless the user changes it.
3. User explicitly selects Telugu:
   - registration/login/onboarding displays Telugu;
   - language persists on refresh/relaunch unless the user changes it.
4. Existing users with a previously persisted valid language may retain that preference, but routing must still respect the intended onboarding/auth state. Do not use persisted language as a reason to bypass required onboarding/navigation.
5. Do not prefill a real-looking phone number from test/debug state on a fresh manual QA launch unless the approved product explicitly requires it. Remove or isolate development-only seed/default values from normal QA startup if confirmed.

## Authorized scope

Focused changes only in Farmer Flutter app startup/routing/localization/persistence and related tests, plus the Farmer QA launcher if it is the source of stale state or duplicate launches. Backend changes are not expected unless a test proves they are required.

## Execute autonomously

1. Follow `AGENTS.md` task-start sync and working-tree safety.
2. Reproduce/diagnose the defect primarily through code inspection and automated tests. Do not repeatedly open Chrome.
3. Inspect app startup route, auth/onboarding route guards, language provider/default locale initialization, shared preferences/browser storage, and any debug/test seed values.
4. Identify the actual root cause; do not merely force English globally.
5. Implement the smallest fix that preserves explicit English/Telugu selection and persistence.
6. Add/adjust automated tests covering at minimum:
   - fresh state begins at intended language/welcome entry, not direct registration;
   - explicit English selection drives English onboarding;
   - explicit Telugu selection drives Telugu onboarding;
   - persisted selection survives provider/app recreation;
   - persisted locale does not incorrectly bypass onboarding/auth routing;
   - no production/QA startup phone-number seed leaks into a fresh registration field, if such a seed caused the observed value.
7. Run Farmer `flutter pub get`, `flutter analyze`, `flutter test`.
8. Run a non-interactive web build/smoke check where practical. Only after all automated checks pass may Codex perform one final interactive Chrome launch, and only if no Farmer QA instance is already running.
9. If the final interactive launch is used, leave it running for the human and do not launch again automatically.
10. Inspect diff and avoid unrelated localization polish/refactors.
11. Commit and push the focused fix on the approved non-main branch.
12. Update and push `docs/AGENT_REPORT.md` with this exact Task ID, root cause, files changed, exact test results, and whether one human Chrome re-check is ready.
13. Stop after publishing PASS/BLOCKED. Do not wait for or repeatedly attempt the complete human end-to-end QA flow.

## Completion criteria

PASS only when automated checks support the corrected initialization/persistence behavior and the Farmer app is ready for one human re-check without Codex repeatedly opening Chrome. If browser storage must be cleared for a true fresh-state retest, update the QA launcher so `test farmer app` provides a reliable clean QA start while preventing duplicate Flutter/Chrome launches.
