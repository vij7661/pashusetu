# PashuSetu Farmer App — APP-1.1 Completion

This build extends APP-1 from basic API connectivity into the main approved Farmer journey.

## Added in APP-1.1
- Operator-created weighment acknowledgement screen
- explicit "I acknowledge" gating
- receipt creation after acknowledgement
- camera image picker + object-storage upload-contract execution
- listing history
- agreement creation / farmer confirmation
- shipment / transaction-state tracking
- dispute screen
- settlement screen
- six-language string scaffold: Telugu, Hindi, English, Marathi, Tamil, Malayalam
- route coverage for the new Farmer screens

## Important boundaries
The mobile client still does not pretend to provide:
- real Aadhaar/KYC verification
- real bank/UPI payout onboarding
- real push/SMS/WhatsApp delivery
- live transporter GPS
- real Bluetooth scale integration

Those require provider/hardware choices and remain behind the backend adapter architecture.

## Run
Android emulator:

```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

Chrome QA from this directory:

```bash
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

Run the Chrome command from `apps/farmer_mobile` (not the repository root), so Flutter can find this app's `pubspec.yaml` and web scaffold.

Backend:
```bash
cd ../../
cp .env.example .env
docker compose up --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.db.seed
```

Development OTP: `4816`
