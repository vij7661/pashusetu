# PashuSetu — Current Agent Task

**Task ID:** `QA-FARMER-KYC-PAYOUT-001`

**Status:** `READY`

**Priority:** QA BLOCKER — execute before further Farmer manual QA.

**Related defects:** GitHub #14 (Payout Setup dead-end, BLOCKER), #15 (duplicate language after OTP, HIGH).

## Product decisions approved for this task

1. New Farmer onboarding must be: **initial language selection -> mobile -> OTP -> Farmer Details/Location -> KYC -> Payout Setup -> Review/Consent -> Farmer ID/Home**. Do not ask for language a second time after OTP.
2. Existing Farmer login must skip registration-only KYC and payout setup.
3. KYC screen must contain actual input fields for the current MVP QA flow instead of a text-only placeholder.
4. Minimal KYC input contract for now:
   - Aadhaar number: exactly 12 digits in the QA UI contract;
   - Name as per Aadhaar: required, trimmed, reasonable min/max length;
   - explicit consent checkbox describing that the identifier is being submitted for identity verification/testing;
   - no biometric collection.
5. **QA only:** use UIDAI-published developer test UIDs, never a real person's Aadhaar. Canonical QA KYC fixtures:
   - `KYC_FARMER_EN_001`: `999941057058`, name `Shivshankar Choudhury`
   - `KYC_FARMER_TE_001`: `999971658847`, name `Kumar Agarwal`
   - `KYC_FARMER_SUB3_001`: `999933119405`, name `Fatima Bedi`
   These are published by UIDAI for developer testing. Keep them isolated to QA/test fixtures.
6. QA KYC behavior must be allowlisted/deterministic: seeded test UID + matching configured fixture may return `QA_VERIFIED`; valid-format but unseeded UID must fail closed with a safe QA message and must not create a verified KYC state.
7. Core/pilot data protection: **do not persist or log the raw Aadhaar number in the normal core application database or logs.** After QA/provider response, core state should retain only what is necessary for the MVP such as masked last4, KYC status, provider/test reference and timestamps. Never display more than masked Aadhaar after submission. Production/provider design remains replaceable/open.
8. Payout Setup must let the Farmer choose **UPI OR Bank Account**; do not require both.
   - UPI fields: UPI ID (required when UPI selected; validate format reasonably, do not make real payment calls).
   - Bank fields: account-holder name, account number, confirm account number, IFSC (required when Bank selected; account numbers must match; validate IFSC format; mask account number after submission/display).
   - QA data is synthetic only. No real payout provider/payment transfer in this task.
9. Registration must not dead-end at KYC or Payout. Valid QA KYC + valid QA payout data must allow the registration wizard to continue to review/consent and complete the current profile/onboarding contract.
10. Preserve safe localized user-facing errors; no Dio/HTTP/raw backend codes/stack traces in UI.

## Compliance/safety basis

- UIDAI defines Masked Aadhaar as hiding the first 8 digits and showing only the last 4.
- UIDAI developer resources publish test UIDs for authentication/e-KYC integration testing.
- Treat production Aadhaar/KYC provider/legal integration as OPEN; this task builds a replaceable QA adapter and UI contract, not a production UIDAI integration.
- Never use real Aadhaar, real bank data, real UPI accounts, real OTP/SMS or payment/payout calls.

## Required implementation

### A. Fix duplicate language step (#15)
- Remove/bypass legacy post-OTP language screen.
- Preserve the initial selected locale through OTP and all following registration steps.
- OTP success for new Farmer goes directly to Farmer Details/Location.
- Existing Farmer goes to Home after successful auth without registration-only screens.

### B. KYC UI and QA adapter
- Replace text-only KYC placeholder with form fields above.
- Digits-only / exact 12-digit Aadhaar input; no prefilled UID.
- Required name and consent validation.
- Implement explicit `KycVerificationService` / adapter boundary if not already present. QA adapter must be isolated/fail closed outside QA/test.
- QA fixture store/database may contain only the official UIDAI test UIDs needed for deterministic testing. Do not copy these into normal/pilot user records.
- On successful QA verification, persist only masked last4 + KYC status + QA/provider reference in core Farmer/profile state.
- Unseeded/invalid/mismatched QA KYC must create no verified state.
- All logs/errors must redact Aadhaar.

### C. Payout UI and state (#14)
- Implement method selection: UPI / Bank.
- UPI validation and synthetic QA submission path.
- Bank holder/account/confirm/IFSC validation; prevent mismatch/invalid format.
- Add replaceable payout-details service/repository boundary. This task stores QA/profile setup state only; no real money movement/provider API.
- Mask bank account number in later display/logs.
- Fix the current Continue dead-end and trace/remove the backend/UI contract mismatch causing the generic 4xx failure.

### D. QA fixtures
Synchronize code fixtures/manual documentation with the canonical QA workbook:
- Farmer mobiles: existing canonical fixtures.
- KYC fixtures listed above.
- Example payout fixtures:
  - `PAY_FARMER_EN_UPI`: `farmer.en@pashusetuqa`
  - `PAY_FARMER_TE_BANK`: holder `Kumar Agarwal`, account `123456789012`, confirm same, IFSC `HDFC0001234`
  - `PAY_FARMER_SUB3_UPI`: `sub3.farmer@pashusetuqa`
- Seed/reset remains isolated to `pashusetu_qa` and fail-closed against any non-QA DB/environment.

## Required tests / boundaries

Add automated regression covering at minimum:
- initial language selected once; OTP success skips duplicate language and preserves locale;
- Aadhaar blank/11/12/13 digits, letters/spaces/paste, missing consent, missing/short name;
- seeded UIDAI test UID + matching fixture -> QA verified;
- valid-format unseeded test UID -> safe QA not-found/unverified, zero verified-state side effect;
- raw Aadhaar absent from normal DB columns/serialized API responses/log output where reasonably testable; only masked last4/status/ref returned after success;
- UPI valid/invalid/blank;
- Bank account blank, mismatch, invalid IFSC, valid synthetic data;
- KYC/Payout repeated submit/busy guard;
- successful full new-Farmer path can proceed through KYC + payout to review/profile completion;
- existing Farmer path skips KYC/payout;
- English and Telugu validation/error strings for critical fields;
- no raw technical exception leakage.

Run Farmer `flutter pub get`, `flutter analyze`, full `flutter test`; relevant backend KYC/profile/auth tests; full backend suite if backend changes; QA DB reset/seed twice to prove determinism; API health; non-interactive web build; secret/sensitive-data scan for accidental Aadhaar/bank logging patterns.

## Evidence handoff

Update `docs/AGENT_REPORT.md` with Task ID, root cause for #14/#15, exact UI/API/state changes, KYC/payout fixture mapping, proof of raw-Aadhaar redaction/non-persistence in core state, exact test counts, commits, known gaps, and a concise manual retest script. Report `CANDIDATE READY FOR QA REVIEW` or `BLOCKED`; do not self-approve final manual QA.

## Scope exclusions

No real UIDAI authentication/e-KYC production integration, biometrics, real Aadhaar data, real bank/UPI accounts, real payment/payout provider, production deployment, pilot DB mutation, Bluetooth work or unrelated marketplace feature development.
