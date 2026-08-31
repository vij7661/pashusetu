# Farmer Mobile Manual QA Runbook

This runbook validates the Farmer MVP against controlled local development fixtures. It is **manual-QA ready**, not pilot/production ready.

## 1. Reset and start the QA backend

From the repository root on Windows:

```bat
copy .env.example .env
docker compose down -v
docker compose up --build -d
docker compose exec api alembic upgrade head
make farmer-qa-seed
```

If `make` is not available on Windows, run:

```bat
docker compose exec api python scripts/seed_farmer_manual_qa.py
docker compose exec api python scripts/seed_farmer_manual_qa_states.py
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

Farmer CI also publishes a debug emulator APK artifact named `pashusetu-farmer-manual-qa-emulator-apk`.

### Physical Android phone

The phone and PC must be on the same network. Build/run with the PC LAN IP:

```bash
cd apps/farmer_mobile
flutter create --platforms=android --project-name pashusetu_farmer .
flutter run --dart-define=API_BASE_URL=http://<PC-LAN-IP>:8000/api/v1
```

Local HTTP is for debug QA only. Do not enable cleartext traffic in a release build.

## 3. Controlled Farmer identities

| Scenario | Mobile | Dev OTP | Expected start |
| --- | --- | --- | --- |
| Brand-new Farmer | `+919100000001` | `8830` | Language → mobile → OTP → Farmer Details → KYC → Home |
| Registration resumed | `+919100000017` | `4856` | OTP → restored Farmer Details → KYC |
| KYC pending Farmer | `+919100000025` | `1735` | Existing login → Home; transaction mutations blocked |
| KYC verified Farmer | `+919100000033` | `0588` | Existing login → full Farmer journey |

These OTPs are deterministic only because local development explicitly opts into the development OTP provider. Production defaults fail closed.

## 4. Seeded Farmer market/transaction data

For `+919100000033`:

- `GOAT-QA-CREATE` — verified/acknowledged weight `50.000 kg`, reserved for Create Listing.
- `PS-LST-QA-OFFER` — Farmer-owned published listing for `GOAT-QA-OFFER`, weight `48.500 kg`.
- `BID-QA-001` — active ₹420/kg offer, total ₹20,370.
- Hyderabad QA recommendation — ₹400/kg.
- `TX-QA-SHIPMENT` — authoritative state `IN_TRANSIT`.
- `TX-QA-DISPUTED` — authoritative state `DISPUTED`.
- `TX-QA-SETTLED` — authoritative state `SETTLED`.

The state fixtures exist only so the Farmer UI can be tested without manually operating Buyer/Operator apps first.

## 5. Manual QA cases

### FQA-01 — Brand-new registration

Use `+919100000001` / `8830`. Choose a language, complete Farmer Details, then submit a 12-digit QA Aadhaar such as `123412341234`.

Expected: permanent Farmer ID exists only after KYC submission; Home opens in `KYC_PENDING`; raw Aadhaar is not returned/stored in the core domain; transactional listing remains blocked until verification.

### FQA-02 — Resume registration

Use `+919100000017` / `4856` through New Farmer Registration.

Expected: saved Farmer Details are restored and the journey resumes at KYC, without a duplicate permanent Farmer account.

### FQA-03 — KYC-pending Home

Use Existing Farmer Login with `+919100000025` / `1735`.

Expected: Home/Profile and livestock management work; Create Verified Listing is disabled; direct transactional mutations return `KYC_VERIFICATION_REQUIRED`.

### FQA-04 — Verified Farmer login

Use `+919100000033` / `0588`.

Expected: Home/Profile load without KYC blocker and Farmer transaction actions are available subject to domain prerequisites.

### FQA-05 — Authoritative verified listing weight

Open Create Verified Listing → Individual Goat → enter `GOAT-QA-CREATE` → load Verified Weight.

Expected: weight is loaded from backend as `50.000 kg`; no fabricated default is displayed; total = authoritative weight × Farmer price; Publish stays disabled until acknowledgement; published listing appears in Your Listings.

### FQA-06 — Farmer-owned listing history and offers

Open Your Listings → `PS-LST-QA-OFFER`.

Expected: only Farmer-owned history is returned; Buyer Offers shows `BID-QA-001`, ₹420/kg, ₹20,370 total and server sequence.

### FQA-07 — Accept offer → transaction

Accept `BID-QA-001`.

Expected: backend accepts the bid, creates/returns the authoritative transaction and the app navigates to Transaction detail at `OFFER_ACCEPTED` instead of losing the transaction ID.

### FQA-08 — Agreement

From the accepted transaction open Agreement, create a proposal, then confirm as Farmer.

Expected: Farmer confirmation is recorded; state remains backend-authoritative and waits for Buyer confirmation when required.

### FQA-09 — Transaction history

Home → Transactions.

Expected: accepted transaction can be rediscovered after navigation/restart. The seeded `TX-QA-SHIPMENT`, `TX-QA-DISPUTED`, and `TX-QA-SETTLED` are also visible.

### FQA-10 — Shipment tracking

Open `TX-QA-SHIPMENT` → Pickup & Delivery.

Expected: `IN_TRANSIT` comes from backend; app does not invent GPS/transporter information.

### FQA-11 — Dispute

Open `TX-QA-DISPUTED` → Dispute and submit a supported reason.

Expected: dispute is tied to the authenticated transaction party; another Farmer cannot mutate it.

### FQA-12 — Settlement

Open `TX-QA-SETTLED` → Settlement.

Expected: gross, adjustment, platform fee and final amount come from backend; repeated settlement load is idempotent; development UI makes no real escrow/payment claim.

### FQA-13 — Weighment acknowledgement

Use an Operator-created weighment in Farmer review state through the approved test setup.

Expected: Farmer acknowledgement is explicit; reject routes domain state to reweigh; accept permits receipt; listing still requires `VERIFIED` weighment.

## 6. Negative/resilience checks

Validate: invalid mobile; invalid/wrong OTP; existing-login on unregistered mobile; duplicate registration; KYC before Farmer Details; KYC-pending transaction block; invalid/non-owned Goat/Lot; target without verified weighment; Publish without acknowledgement; invalid price/window; backend unavailable; and all six language layouts (Telugu, Hindi, English, Marathi, Tamil, Malayalam).

## 7. Defect evidence

For every defect record: case ID, device/emulator and Android version, app commit/artifact, account, exact steps, expected/actual result, screenshot/video, backend error code/message, and reset/reproduction status.

Do not change production/domain behavior solely to satisfy a manual expectation. Classify each failure against product contract, code, fixture/test data, test expectation and environment.

## 8. Development-only boundaries

Outside this manual-QA acceptance: production OTP, compliant live Aadhaar/KYC provider, real UPI/bank payout, real payment/escrow, live WhatsApp/SMS/push, real Bluetooth livestock scale, physical QR printer and live transporter GPS/maps.

Manual-QA ready means the Farmer software flow is testable end-to-end against the controlled development backend. It does not mean pilot/production ready.
