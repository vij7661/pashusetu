# PashuSetu — Current Agent Task

**Task ID:** `QA-FARMER-OTP-UX-001`

**Status:** `READY`

**Priority:** QA BLOCKER — execute before unrelated feature work.

**Work item:** Farmer OTP negative-path UX and safe error mapping

## Defect observed in manual QA

On the Farmer OTP screen, entering a wrong OTP correctly reaches backend rejection, but the UI exposes the raw transport/exception text:

`DioException [bad response]: null`
`Error: OTP_INVALID: Invalid OTP.`

This is not acceptable user-facing behavior. Expected business validation failures must be rendered as friendly localized UI messages, while technical exception details remain available only to development logs/diagnostics where appropriate.

## Required behavior

1. Wrong OTP must keep the user on the OTP screen and show a concise localized message such as `Invalid OTP. Please try again.` in English and the approved Telugu equivalent from localization resources.
2. Do not display `DioException`, HTTP internals, stack traces, backend exception class names, raw response objects, or duplicated `Error:` prefixes to the user.
3. Preserve backend error codes internally and map known auth codes to stable domain/UI errors. At minimum inspect and handle `OTP_INVALID`, `OTP_EXPIRED`, already-used/reused OTP, resend/rate-limit states if those codes exist, and generic network/server failure.
4. Wrong OTP must not authenticate, navigate forward, corrupt the current challenge, or silently reset the form. Preserve the existing backend attempt policy.
5. Correct QA OTP `4816` for a seeded canonical QA user must still succeed after the fix.
6. Error text must follow the currently selected locale and must not force a locale change.
7. Unknown/unexpected failures must show a safe generic localized message (for example `Something went wrong. Please try again.`), while retaining diagnostic details in debug logging only.
8. Do not weaken OTP security or change the deterministic QA-only OTP contract.

## Tests required

Add/adjust focused tests covering:
- wrong OTP -> localized friendly invalid-OTP message, no raw Dio/exception text, no navigation;
- expired OTP -> localized expired message;
- used/reused OTP -> localized safe message;
- network/server/unknown error -> localized generic message without raw exception leakage;
- correct seeded QA OTP `4816` -> success path remains green;
- English and Telugu negative-path rendering;
- existing OTP attempt/resend semantics remain green.

Run Farmer `flutter analyze` and full `flutter test`; run focused auth/backend tests if any backend contract change is actually required. Prefer a Flutter error-mapping/UI fix if the backend is already returning stable codes. Do not redesign auth unnecessarily.

## Scope and safety

Focused Farmer auth repository/controller/UI/localization/tests only, plus backend auth only if a confirmed contract defect exists. Do not modify marketplace rules, QA fixture numbers, QA database isolation, real SMS, KYC, payments, Bluetooth, production deployment, or pilot data.

Follow `AGENTS.md` sync/working-tree safety. Do not repeatedly launch Chrome while fixing. Commit/push the focused patch and update `docs/AGENT_REPORT.md` with this exact Task ID, root cause, files changed, exact test results and whether one human OTP re-check is ready. Stop after PASS/BLOCKED.

## Completion criteria

PASS only when expected OTP failures are presented as localized domain messages with no raw Dio/technical exception leakage, correct OTP still succeeds, tests are green, and the Farmer OTP screen is ready for one manual QA re-check.
