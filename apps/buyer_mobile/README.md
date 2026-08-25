# PashuSetu Buyer App — APP-2

Flutter Buyer application connected to the TD-8 backend.

## Implemented
- shared Welcome page
- New Buyer Registration
- Existing Buyer Login
- Buyer Profile
- verified marketplace search
- weight filters
- verified listing view
- buyer offer ₹/kg
- idempotency key per bid intent
- backend-calculated total offer
- authoritative server sequence display
- active bid view
- agreement review and Buyer confirmation
- secured-funds screen
- delivery verification
- tolerance result
- settlement / dispute routing
- dispute screen
- settlement screen
- six-language string scaffold

## Backend ownership
The Buyer app does not decide:
- bid ordering
- auction close
- accepted bid
- agreement lock
- payment state
- delivery tolerance
- settlement amount

These are returned by the backend.

## Run
```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

Backend:
```bash
cd ../../
cp .env.example .env
docker compose up --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.db.seed
```

Development OTP: `4816`

## Current provider boundaries
- Buyer KYC is provider-dependent.
- Secured funds uses the backend simulated provider.
- Delivery weighment must come from the verified Operator/scale workflow.
- SMS/WhatsApp/push and live logistics require selected providers.
