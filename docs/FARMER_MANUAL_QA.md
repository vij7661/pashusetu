# Farmer Mobile Manual QA Runbook

This runbook is for local/manual validation of the Farmer MVP. It uses simulated development providers and controlled QA fixtures. It is **not** a pilot/production deployment guide.

## 1. Reset and start the QA backend

From the repository root:

```bash
copy .env.example .env
# macOS/Linux: cp .env.example .env

docker compose down -v
docker compose up --build -d
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_farmer_manual_qa.py
```

The QA seed refuses to run outside `local`, `test`, or `development`. It never persists raw Aadhaar.

Backend API: `http://localhost:8000/api/v1`

## 2. Run the Farmer app

### Android emulator

```bash
cd apps/farmer_mobile
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

The Farmer CI workflow also publishes a debug emulator APK artifact named:

`pashusetu-farmer-manual-qa-emulator-apk`

### Physical Android phone

The phone and development PC must be on the same network. Replace `<PC-LAN-IP>` with the PC's LAN address:

```bash
cd apps/farmer_mobile
flutter create --platforms=android --project-name pashusetu_farmer .
flutter run --dart-define=API_BASE_URL=http://<PC-LAN-IP>:8000/api/v1
```

For local HTTP testing on a physical device, use a debug Android manifest that enables cleartext traffic. Do not enable cleartext traffic for a release build.

## 3. Controlled Farmer QA identities

| Scenario | Mobile | Development OTP | Expected start |
| --- | --- | --- | --- |
| Brand-new Farmer | `+919100000001` | `8830` | Language → mobile → OTP → Farmer Details → KYC → Home |
| Registration resumed | `+919100000017` | `4856` | Mobile → OTP → KYC with saved Farmer Details |
| KYC pending Farmer | `+919100000025` | `1735` | Existing Farmer Login → Home; transactional mutations blocked |
| KYC verified Farmer | `+919100000033` | `0588` | Existing Farmer Login → full Farmer transactional journey |

OTP values are deterministic only because `APP_ENV=local` and `DEVELOPMENT_OTP_SEED` is explicitly configured for development. Production defaults fail closed.

## 4. Seeded verified-market data

For the verified Farmer (`+919100000033`):

- `GOAT-QA-CREATE` — verified and acknowledged weight `50.000 kg`; use this to test **Create Verified Listing**.
- `PS-LST-QA-OFFER` — already-published Farmer-owned listing for `GOAT-QA-OFFER`, verified weight `48.500 kg`.
- `BID-QA-001` — active buyer offer on `PS-LST-QA-OFFER`, ₹420/kg, total ₹20,370.
- Hyderabad QA market recommendation — ₹400/kg.

The Create Listing screen must load verified weight from the backend. It must never display a fabricated default weight.

## 5. Manual QA cases

### FQA-01 — Brand-new registration

1. Choose a language.
2. Register `+919100000001` with OTP `8830`.
3. Enter Farmer Details.
4. Enter any 12-digit QA Aadhaar value, for example `123412341234`.
5. Submit KYC.

Expected:
- permanent Farmer ID is created only after KYC submission;
- Home opens with `KYC_PENDING` messaging;
- raw Aadhaar is not returned by APIs or shown in Profile;
- Create Verified Listing remains disabled while KYC is pending.

### FQA-02 — Resume incomplete registration

1. Start New Farmer Registration with `+919100000017`, OTP `4856`.
2. Verify OTP.

Expected:
- previously saved Farmer Details are restored;
- flow resumes at KYC rather than creating a duplicate registration/account.

### FQA-03 — Existing KYC-pending Farmer

1. Existing Farmer Login with `+919100000025`, OTP `1735`.
2. Open Home and Profile.
3. Add an individual Goat or Lot.

Expected:
- Home and livestock management are available;
- Create Verified Listing is disabled;
- if a transactional API is attempted directly, backend returns `KYC_VERIFICATION_REQUIRED`.

### FQA-04 — Existing verified Farmer login

1. Existing Farmer Login with `+919100000033`, OTP `0588`.
2. Confirm Home and Profile load without a KYC-pending blocker.

Expected: full Farmer transaction actions are enabled subject to normal domain prerequisites.

### FQA-05 — Create verified listing with authoritative weight

1. Open Create Verified Listing.
2. Choose `Individual Goat`.
3. Enter `GOAT-QA-CREATE`.
4. Load Verified Weight.
5. Confirm `50 kg` comes from backend eligibility.
6. Use market recommendation or enter a price.
7. Confirm total = verified weight × price/kg.
8. Confirm Publish is disabled before acknowledgement.
9. Acknowledge and publish.

Expected:
- no hard-coded/default 50 kg is shown before eligibility is loaded;
- server remains authoritative for weight and total;
- published listing appears under **Your Listings** only for this Farmer.

### FQA-06 — Farmer-owned listing history and Buyer Offers

1. Open Your Listings.
2. Open `PS-LST-QA-OFFER`.

Expected:
- listing is visible because it belongs to the logged-in Farmer;
- unrelated Farmers' listings are not shown;
- Buyer Offers shows `BID-QA-001` with ₹420/kg and total ₹20,370;
- server sequence is shown.

### FQA-07 — Accept offer and create transaction

1. From `PS-LST-QA-OFFER`, accept `BID-QA-001`.

Expected:
- accepted bid is recorded server-side;
- Farmer app creates/loads the authoritative transaction;
- app navigates to Transaction detail instead of losing the transaction ID;
- transaction state begins at `OFFER_ACCEPTED`.

### FQA-08 — Agreement navigation

From the accepted transaction, open Agreement.

Expected:
- Farmer can create agreement proposal;
- Farmer confirmation is recorded;
- state remains backend-authoritative and waits for Buyer confirmation where required.

### FQA-09 — Transaction history persistence

1. Return to Home.
2. Open Transactions.
3. Open the transaction created in FQA-07.

Expected: the transaction can be rediscovered after navigation/restart without manually knowing its ID.

### FQA-10 — Weighment acknowledgement route

For an operator-created Farmer review weighment, open `/weighment/<id>/ack` through the normal test setup.

Expected:
- acknowledgement is explicit;
- rejecting a weighment routes domain state to reweigh, not listing;
- accepting permits receipt generation;
- listing remains dependent on a `VERIFIED` weighment.

### FQA-11 — Shipment tracking

For a transaction progressed by the Buyer/Operator test setup, open Pickup & Delivery.

Expected:
- screen renders authoritative transaction state;
- it does not invent live GPS or transporter data;
- delivery/tolerance/dispute result follows backend state.

### FQA-12 — Dispute

For a transaction in `DISPUTED`, open Dispute.

Expected:
- Farmer can open the transaction's dispute with supported reason;
- user cannot mutate a dispute belonging to another transaction party;
- resolution/reweigh remains authoritative server behavior.

### FQA-13 — Settlement

For `RESOLVED` or `SETTLED` transaction state, open Settlement.

Expected:
- gross, adjustment, platform fee and final amount come from backend;
- repeated settlement load is idempotent;
- no real payment/escrow claim is shown in this development build.

## 6. Negative and resilience checks

Test all of these:

- invalid mobile format;
- OTP fewer/more than four digits;
- wrong OTP;
- expired/exhausted OTP attempts where practical;
- Existing Farmer login for an unregistered mobile;
- New registration for an already-registered Farmer;
- KYC submission before Farmer Details via API must fail;
- KYC-pending Farmer transaction mutation must fail;
- invalid/non-owned Goat or Lot code when loading listing eligibility;
- target with no verified weighment must fail with `VERIFIED_WEIGHMENT_REQUIRED`;
- publish without acknowledgement remains disabled in UI;
- invalid listing price/window rejected by backend;
- backend stopped/unreachable shows an error and app remains responsive;
- rotate through Telugu, Hindi, English, Marathi, Tamil and Malayalam; report untranslated or clipped text.

## 7. Evidence to record for every defect

Record:

- case ID;
- phone/emulator model and Android version;
- app commit/build artifact;
- account/mobile used;
- exact steps;
- expected result;
- actual result;
- screenshot/video;
- backend error code/message if visible;
- whether issue reproduces after reset.

Do not change production/domain behavior solely to make a manual expectation pass. Each defect must be classified against the product contract, implementation, fixture/test data, test expectation and environment.

## 8. Development-only boundaries

This manual-QA build intentionally uses simulated or incomplete external integrations. The following remain outside Farmer manual-QA acceptance and require provider/hardware selection before pilot:

- production OTP provider;
- compliant live Aadhaar/KYC provider;
- real UPI/bank payout provider;
- real payment/escrow integration;
- live WhatsApp/SMS/push provider;
- real Bluetooth livestock scale integration;
- physical QR printer validation;
- live transporter GPS/maps provider.

Manual-QA readiness means the Farmer software flow is testable end-to-end against the controlled development backend. It does not mean production/pilot readiness.
