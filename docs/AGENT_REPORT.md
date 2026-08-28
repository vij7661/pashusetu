# PashuSetu — Farmer KYC/Payout QA Evidence

- **Task ID:** `QA-FARMER-KYC-PAYOUT-001` (GitHub #14, #15)
- **Timestamp:** 2026-08-28T12:21:32+05:30
- **Branch:** `feat/issue-4-local-backend-farmer-integration`
- **Status:** `PASS — CANDIDATE READY FOR QA REVIEW`
- **Implementation commit:** `10a897dff191cdaf799b1fa3d9af2e547a91c282`
- **Objective:** Remove duplicate post-OTP language selection and complete QA-only KYC/payout onboarding. Independent human QA owns final acceptance.

## Root causes and fixes

| Defect | Root cause | Fix/evidence |
| --- | --- | --- |
| #15 duplicate language | Registration repeated the language chooser already completed on welcome | Legacy step bypassed. `auth_flow_test.dart` proves OTP goes directly to Farmer Details, preserves English, and completes the full wizard. |
| #14 payout dead-end | KYC/payout were placeholders and profile POST had no supporting contract | Added actual KYC, UPI/bank, validation, busy guards, masked review/consent, QA verification endpoint, adapters, and atomic profile completion. Integration proves final `201`. |

## Contract and data protection

- New Farmer sequence: welcome language → mobile → OTP → details/location → KYC → one payout method → masked review/consent → Home. Existing Farmer remains OTP → Home.
- KYC is empty by default and requires exactly 12 digits, trimmed 2–120 character matching QA name, and explicit consent. The QA-only `KycVerificationService` uses the fixture IDs in `docs/QA_FIXTURES.md`, is isolated/fail-closed, and returns `QA_KYC_NOT_FOUND` for unseeded/mismatched input.
- Payout supports either validated synthetic UPI or Bank holder/matching 6–18 digit accounts/IFSC. Account fields are obscured.
- Core persistence contains only KYC status, masked last four, provider reference, payout status/method, and masked reference. Database inspection found no raw identifier or bank-account column. API tests assert full inputs are absent from responses. Identity source contains no logging/print call.
- Fixture mapping: `KYC_FARMER_EN_001` → English/UPI, `KYC_FARMER_TE_001` → Telugu/Bank, `KYC_FARMER_SUB3_001` → sub-3/UPI. Exact official test inputs remain only in the approved QA fixture source/documentation. Expected output is masked (for example `XXXXXXXX8847` and `XXXXXXXX9012`).

## Exact validation

| Gate | Result |
| --- | --- |
| `flutter pub get` | PASS, exit 0; 12 newer incompatible-version notices only |
| `flutter analyze` | PASS, no issues; final focused rerun 106.6s |
| Full `flutter test` | PASS, **27 passed**, exit 0 |
| Focused final Flutter | PASS, **7 passed** |
| Focused backend registration/KYC | PASS, **2 passed**, 1 Starlette warning |
| Full backend `pytest -q` | PASS, **69 passed**, 1 Starlette warning, 10.37s |
| Focused Ruff | PASS; existing FastAPI B008/seed UP017 excluded consistently |
| Alembic | PASS; migration `0010_farmer_kyc_payout` applied |
| QA reset/seed twice | PASS both; each: 6 users, 2 farmers, 1 buyer, 6 goats, 2 lots, 1 listing |
| API health | PASS; HTTP 200, environment `qa` |
| Web build | PASS; `Built build\\web`; Wasm suggestion and existing Cupertino font warning only |
| Diff/redaction | PASS; diff check clean, no identity logging, response/database masked |

## Changed areas

Farmer registration/localization/error mapping, identity repository, validators and tests; backend identity schemas/router/service/model, QA KYC/payout adapters and migration; QA fixtures/seed, integration/schema tests, and QA documentation.

## Known gaps / manual required

- The already-open Chrome session predates this implementation. Relaunch is required for new UI visuals, back/refresh, keyboard/pointer, and Telugu layout.
- Wizard draft data is memory-only and not promised to survive full refresh.
- Android/device validation was not run; web evidence is not Android-pilot proof.
- Production UIDAI/legal/provider integration, biometrics, real payouts, and real sensitive data remain excluded.

## Manual retest

1. Relaunch using `test farmer app`; choose Telugu once and start New Farmer Registration with the canonical Telugu mobile/OTP from `docs/QA_FIXTURES.md`.
2. Confirm OTP goes directly to Farmer Details with Telugu preserved and no second language screen.
3. At KYC, exercise blank/11/13 digits, missing/short name, and missing consent; confirm friendly errors.
4. Exercise the documented unseeded QA input; confirm safe rejection and no profile/navigation. Then use `KYC_FARMER_TE_001` exactly as documented and continue.
5. Verify invalid/blank UPI, then Bank blank/mismatch/invalid IFSC. Enter `PAY_FARMER_TE_BANK` from the work order/fixture document.
6. Confirm review contains only masked KYC/account values; consent and submit. Repeated clicks while busy must not duplicate creation.
7. Confirm Home opens. Login with existing `FARMER_EN_001`; confirm it skips KYC/payout and goes Home.
8. Confirm no Dio/backend codes/raw JSON appear; repeat critical visuals in English.

No prohibited/destructive action, pilot/production mutation, real sensitive input, payment call, deployment, merge, force-push, or history rewrite occurred. Working tree was clean after implementation commit; report commit follows. Recommended next action: independent manual QA.

---

# Prior report — Farmer Manual-Gate Evidence Package

- **Task ID:** `QA-FARMER-MANUAL-GATE-001`
- **Objective:** Remove technical exception leakage, harden implemented Farmer form boundaries, and publish evidence for independent manual-QA review.
- **Timestamp:** 2026-08-28T03:21:07+05:30
- **Branch:** `feat/issue-4-local-backend-farmer-integration`
- **Status:** `PASS — CANDIDATE READY FOR QA REVIEW`
- **Implementation commit:** `97a00fa4ddb427c451e0e47dd86003ad8e464830`
- **Decision owner:** Independent reviewer/human QA. This report is not final manual acceptance.

## Requirements traceability matrix

| Farmer screen/action | Contract reviewed | Positive evidence | Negative/boundary evidence | Result |
| --- | --- | --- | --- | --- |
| Welcome/language | Fresh launch stays on welcome; explicit English/Telugu; persistence must not bypass onboarding | `onboarding_initialization_test.dart`: English/Telugu selection and provider recreation | Fresh storage, persisted Telugu routing, no seeded phone/OTP | Automated PASS; refresh visuals MANUAL REQUIRED |
| Login mobile | Empty local field; exactly 10 digits; prefixes 6/7/8/9; no fixture autofill | `mobile_number_test.dart`, `auth_flow_test.dart` | Blank/9/11+, 0–5 prefix, letters/symbols/spaces/`+91`; invalid input makes zero repository calls | Automated PASS |
| OTP request | Seeded fixture proceeds; unseeded valid fixture fails without challenge | `test_qa_otp_lifecycle.py`, `test_auth_otp_safety.py` | `QA_TEST_USER_NOT_FOUND`; invalid format/prefix; no challenge side effect | Automated PASS |
| OTP verify/navigation | Correct QA OTP `4816` authenticates; server remains authoritative | `auth_flow_test.dart` reaches dashboard; backend lifecycle returns role-bearing token | Blank/malformed stays local with zero verify calls; wrong/expired/reused/attempt-limit mappings; wrong OTP stays on login | Automated PASS |
| Farmer registration/details | Role-only canonical Farmer can authenticate and create one pending profile; full name minimum 2 | `test_qa_farmer_registration.py` exercises OTP → authenticated profile POST | Empty/one-character name blocked in UI; duplicate profile behavior remains backend-controlled | API PASS; complete browser wizard MANUAL REQUIRED |
| Profile | Authenticated Farmer profile is loaded from API | Backend registration/profile response integration | Transport/API failure goes through safe localized boundary | Code/API PASS; visual MANUAL REQUIRED |
| Goat creation | Backend Goat schema and authenticated ownership path | Existing backend livestock integration | API errors no longer render raw exceptions; empty optional breed accepted by contract | Backend PASS; UI submit MANUAL REQUIRED |
| Lot creation | Quantity must be integer 1–500 | Existing backend livestock integration | `numeric_validation_test.dart`: empty, 0, 1, 500, 501, negative, decimal, spaced and alphabetic | Automated boundary PASS; UI/API MANUAL REQUIRED |
| Weighment acknowledgement/reweigh | Acknowledgement required; backend lock/history authoritative | `test_livestock_weighment_flow.py` | Button disabled until acknowledgement; failures use safe message; reweigh contract covered backend | Backend/code PASS; visual/repeated click MANUAL REQUIRED |
| Listing creation | Target owned by Farmer; verified locked weight is server-authoritative; positive price | Existing marketplace integration and `listing_math_test.dart` | Removed fake 50 kg/₹400 defaults; price empty/0/negative/decimal rejected; repeated publish disabled while busy | Automated/backend PASS; visual target entry MANUAL REQUIRED |
| Listing history/offers | API-authoritative listing/bid sequence; exactly one accepted offer | `test_marketplace_bidding_flow.py`, priority/idempotency tests | Empty/error states safe; backend simultaneous acceptance/idempotency protections exercised | Backend PASS; Farmer UI acceptance MANUAL REQUIRED |
| Agreement | Approved pilot tolerance exactly 1.5%; pickup/final scale required; immutable backend version/state | TD5 agreement/state tests | `numeric_validation_test.dart`: 1.4/1.5/1.6 and location length; removed fixture pickup/scale autofill; buttons busy-guarded | Automated/backend PASS; full two-party UI MANUAL REQUIRED |
| Shipment/transaction status | Server-authoritative transaction state | TD5–TD8 transaction/evidence suites | API failures render generic localized safe messages | Backend PASS; UI lifecycle/native evidence MANUAL REQUIRED |
| Dispute/settlement | Non-negative disputed amount; server settlement/audit rules | TD7 dispute/settlement tests | Blank/negative/decimal dispute amounts rejected; failures sanitized | Automated/backend PASS; UI MANUAL REQUIRED |

## Defect ledger

| Severity | Defect/root cause | Fix | Regression evidence | Commit |
| --- | --- | --- | --- | --- |
| High | Wrapped `DioException`/`OTP_INVALID` was rendered with `toString()` | Central localized error mapper; auth screens never render exception objects | `auth_error_message_test.dart`, `auth_flow_test.dart` | `97a00fa` |
| High | OTP field accepted empty, letters and malformed length before API | Rejecting digits formatter plus 4–8 digit preflight; failed validation has zero repository calls | `auth_flow_test.dart` | `97a00fa` |
| Medium | Login labels/errors were English-only and backend-oriented | Added English/Telugu labels and domain messages | `auth_error_message_test.dart`, localization key coverage via full Flutter suite | `97a00fa` |
| Medium | Other Farmer screens also rendered raw exception strings | Applied the safe localized error boundary to profile, livestock, listing/history/offers, weighment, agreement, transaction/shipment, dispute and settlement error paths | Source leak scan; mapper tests | `97a00fa` |
| High | Lot quantity used `int.parse` without empty/type/range protection | Rejecting numeric input and exact backend 1–500 validation | `numeric_validation_test.dart` | `97a00fa` |
| High | Listing UI displayed hard-coded “verified” 50 kg and ₹400 values and accepted zero price | Removed fabricated weight/price defaults; weight remains server-authoritative; positive price validation and busy guard | `numeric_validation_test.dart`, marketplace backend suite | `97a00fa` |
| High | Agreement prefilled fixture-specific pickup/scale and allowed parse/repeat-submit failures | Empty user-entered locations, approved 1.5% validation, localized validation, busy guards | `numeric_validation_test.dart`, TD5 backend tests | `97a00fa` |
| High | Every allowlisted Farmer already had a profile, preventing a positive registration run | `FARMER_TE_001` is now a role-only user; unverified goat remains synthetic under verified fixture Farmer | `test_qa_farmer_registration.py` | `97a00fa` |

## Error-message matrix

| Backend/domain condition | English | Telugu | Expected state/navigation |
| --- | --- | --- | --- |
| `OTP_INVALID` | The OTP is incorrect. Please try again. | OTP తప్పుగా ఉంది. మళ్లీ ప్రయత్నించండి. | Stay on OTP/login step; no token/navigation |
| `OTP_EXPIRED` | The OTP has expired. Request a new OTP. | OTP గడువు ముగిసింది. కొత్త OTP కోరండి. | Stay on OTP step |
| `OTP_NOT_FOUND` / reused | No active OTP. Request a new OTP. | సక్రియ OTP లేదు. కొత్త OTP కోరండి. | Stay on OTP step |
| `OTP_ATTEMPTS_EXCEEDED` | Too many attempts. Request a new OTP. | చాలా ప్రయత్నాలు చేశారు. కొత్త OTP కోరండి. | Stay on OTP step |
| `QA_TEST_USER_NOT_FOUND` | This mobile number is not registered for QA testing. | ఈ మొబైల్ నంబర్ QA పరీక్ష కోసం నమోదు కాలేదు. | Stay on mobile step; zero challenge |
| `OTP_PROVIDER_UNAVAILABLE` | OTP service is unavailable. Please try again later. | OTP సేవ అందుబాటులో లేదు. తరువాత మళ్లీ ప్రయత్నించండి. | Stay on current step |
| Connection/timeout/offline | Unable to connect to PashuSetu… | Telugu connection guidance | Stay on current step; retry permitted |
| HTTP 5xx | Server error. Please try again later. | సర్వర్ లోపం. తరువాత మళ్లీ ప్రయత్నించండి. | Stay on current step |
| Other HTTP 4xx | Unable to complete the request. Check your details. | అభ్యర్థనను పూర్తి చేయలేకపోయాం… | Stay on current step |
| Unknown client failure | Something went wrong. Please try again. | ఏదో తప్పు జరిగింది. మళ్లీ ప్రయత్నించండి. | Stay on current step |

`auth_error_message_test.dart` asserts these mappings and checks output lacks `DioException`, `OTP_`, `StateError`, and raw-JSON braces. A source scan found no remaining exception `toString()` rendering in Farmer screen error paths; the only remaining `e.toString()` converts livestock JSON ID elements, not exceptions or UI errors.

## API and side-effect evidence

- Invalid mobile and malformed OTP: `auth_flow_test.dart` asserts zero repository/API calls.
- Valid unseeded QA mobile: backend tests assert HTTP 404 `QA_TEST_USER_NOT_FOUND` and zero OTP challenges.
- Wrong OTP: backend increments/preserves attempts and issues no token; widget remains on Login and shows no raw code.
- Expired OTP and consumed/reused OTP: backend rejects with `OTP_EXPIRED` / `OTP_NOT_FOUND`.
- Resend: previous active challenge is consumed and exactly one active latest challenge remains. No separate rate-limit contract currently exists; none was invented.
- Repeated auth submit: loading state disables the button. Listing/agreement mutations now have explicit busy guards. Trust-critical bid acceptance/idempotency remains backend-authoritative and is covered by the existing bidding integration suite.
- Successful canonical registration: `FARMER_TE_001` authenticates with `4816`, creates one pending Telugu Farmer profile, and test cleanup restores role-only state.

## State/navigation matrix

| Scenario | Expected/preserved state | Evidence |
| --- | --- | --- |
| Fresh launch | Welcome/language screen; no registration bypass or seeded fields | Widget PASS |
| English/Telugu selection | Selected locale drives onboarding and persists | Widget/provider PASS |
| App/provider recreation | Valid locale persists, but route remains welcome | Widget/provider PASS |
| Browser URL refresh | Router overrides stale platform location to `/` | Code + widget route PASS; browser visual MANUAL REQUIRED |
| Back during wizard | Standard router/browser back behavior | MANUAL REQUIRED |
| Failed mobile/OTP | Current step retained; no dashboard navigation | Widget PASS |
| Successful login OTP | Token result accepted and route becomes `/home` | Widget + API PASS |
| Successful new profile flow | Role-only Telugu fixture can create pending profile | API PASS; complete wizard MANUAL REQUIRED |
| Refresh during in-progress registration | Controllers are not persisted across refresh | Known behavior; MANUAL REQUIRED to assess UX acceptance |

## Exact validation results

- Farmer `flutter pub get`: passed; 12 newer incompatible package versions reported informationally.
- Farmer `flutter analyze`: `No issues found! (ran in 8.6s)` final gate.
- Farmer full `flutter test`: `22 passed`.
- Farmer focused auth/boundary gate: `14 passed`; earlier focused auth-only rerun: `7 passed`.
- Farmer web build: `Built build\web` in `141.4s`; informational Wasm suggestion and existing CupertinoIcons font warning only.
- Backend focused auth/registration lifecycle: `14 passed`, one upstream Starlette/httpx deprecation warning, in `6.29s`.
- Backend full isolated-QA suite: `68 passed`, one upstream Starlette/httpx deprecation warning, in `10.79s`.
- Focused Ruff after import correction: `All checks passed!`.
- Final guarded `pashusetu_qa` reset/migrate/seed: passed; counts `6 users / 2 Farmer profiles / 6 goats / 2 lots / 1 listing` (the Telugu registration user intentionally has no profile).
- API health: HTTP 200, environment `qa`.
- `git diff --check`: passed; focused credential/private-key scan found no matches.

## Changed files/modules

- Farmer auth error mapping, localized strings, login/registration validation, OTP formatter.
- Safe error rendering across implemented Farmer golden-path screens.
- Numeric/form validation for lot, listing, agreement and dispute actions.
- Auth/error/navigation/boundary Flutter regression tests.
- Canonical QA seed state and real OTP-to-profile integration test.
- QA fixture documentation.

## Known gaps / not tested

- **MANUAL REQUIRED:** No screenshots were captured. The task prohibited repeated Chrome launches; the earlier QA process was not treated as evidence for newly compiled code, and no fabricated visual proof is included.
- **MANUAL REQUIRED:** Full browser wizard rendering, back navigation, browser refresh mid-form, focus/keyboard behavior, screen sizes and Telugu visual layout.
- **MANUAL REQUIRED:** Farmer UI flows for actual goat/lot submission, weighment acknowledgement/reweigh, listing publish, offer acceptance, agreement confirmation, shipment, dispute and settlement. Their backend contracts are automated, but UI E2E is not claimed.
- **MANUAL REQUIRED:** Android device/emulator, camera/evidence, permissions, lifecycle and all native behavior. Web success is not Android pilot readiness.
- Several later transaction/agreement/shipment surfaces retain English-only static business copy; error messages are safe/localized, but full Telugu product-copy completeness was not expanded beyond approved existing localization scope.
- No resend button/rate limiter exists in the current Farmer UI/auth contract. Backend resend invalidation is tested; no new product behavior was invented.
- In-progress registration form data is not persisted across a full browser refresh.

## Manual reviewer script

1. Run `powershell -ExecutionPolicy Bypass -File .\tools\start_farmer_qa.ps1`. Expect the guarded `pashusetu_qa` reset, API health, and one Chrome launch.
2. Confirm the welcome screen appears with empty language selection and no phone value. Select English; refresh once. Expect welcome to remain and English to remain selected.
3. Choose Existing Customer Login. Confirm mobile and OTP fields are empty.
4. Enter `5123456789`. Expect `Invalid mobile number`; no OTP step.
5. Enter valid but unseeded `9999999999`. Expect “This mobile number is not registered for QA testing,” with no raw code/JSON.
6. Enter canonical English Farmer `6123456789`; send OTP. Enter `0000`. Expect “The OTP is incorrect. Please try again,” remain on Login, and no `DioException`/`OTP_INVALID` text.
7. Replace OTP with `4816`. Expect navigation to Farmer Dashboard. Open Profile and confirm canonical synthetic Farmer data loads.
8. Reset via the launcher once before registration testing. Select Telugu and New Farmer Registration. Enter role-only fixture `7234567890`, then OTP `4816`. Expect Telugu steps and no technical errors.
9. At Farmer details, try an empty/one-character full name; expect localized validation. Then enter a synthetic name plus QA village/mandal/district and complete the existing review flow. Expect one pending Farmer profile and dashboard navigation.
10. Add Goat/Lot: confirm fields have no fixture breed/quantity values. For a lot try `0`, `501`, letters, then `1`; expect only 1–500 accepted.
11. Open listing creation. Confirm there is no hard-coded verified weight or ₹400 price. Verify empty/zero price is rejected and repeated publish cannot be tapped while loading.
12. Exercise acknowledgement/listing/offers/agreement/status surfaces using canonical fixture codes in `docs/QA_FIXTURES.md`; record screenshots and any mismatch as independent QA evidence.

## Safety

No prohibited action occurred. Destructive reset ran only through the authorized identity-guarded `pashusetu_qa` workflow. No pilot/production database, real SMS/phone, Aadhaar/KYC data, payment credential, secret, production deployment, merge to `main`, force-push, volume deletion, or system/browser security configuration was used or changed.
