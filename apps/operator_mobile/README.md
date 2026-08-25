# PashuSetu Operator App — APP-3

Flutter Operator application connected to the same TD-8 backend used by Farmer and Buyer.

## Implemented
- Operator OTP login
- Centre dashboard
- Scale status display
- Farmer / Goat / Lot lookup
- individual Goat and Lot support
- vendor-neutral ScaleAdapter
- simulated Bluetooth scale
- live raw readings
- stable-reading detection
- backend reading submission
- stable-weight lock
- verification-video capture screen
- farmer review
- correct reject → fresh reweigh path
- accept → Farmer acknowledgement handoff
- pickup verification
- dispute/controlled reweigh

## Critical flow
```text
Goat/Lot
→ Scale A-114
→ live samples
→ stable?
    no → keep reading
    yes → backend lock
→ verification video
→ Farmer review
→ rejects → new reweigh
→ accepts → Farmer app acknowledgement
```

There is no Operator/Farmer-acknowledgement loop back to the scale after acceptance.

## Hardware boundary
`SimulatedScaleAdapter` is included for development.

A real physical Bluetooth scale adapter must replace it once the livestock scale vendor/model/protocol is selected.

## Current media boundary
Video capture is implemented on the Operator device, but production upload must use the signed object-storage contract once that adapter is selected.

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

Development operator mobile: `+919876500017`
Development OTP: `4816`
