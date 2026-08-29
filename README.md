# PashuSetu — TD-8 Hardened End-to-End MVP

Implementation scaffold derived from **PashuSetu Technical Design v1.0**.

## What is included
- FastAPI modular-monolith backend
- PostgreSQL + SQLAlchemy 2.x
- Alembic migration baseline
- OTP authentication abstraction with a development provider
- JWT access/refresh token scaffolding
- Role-based access control (Farmer, Buyer, Operator, Admin)
- User + role + refresh-session persistence
- Common API response/error conventions
- Request/correlation ID middleware
- `/api/v1` routing
- Dockerfile + Docker Compose
- Pytest test structure
- Initial OpenAPI-ready endpoints
- Placeholders for the approved PashuSetu modules

## Repository shape

```text
pashusetu/
├── apps/
│   ├── farmer_mobile/
│   ├── buyer_mobile/
│   ├── operator_mobile/
│   └── admin_web/
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   ├── identity/
│   │   ├── livestock/
│   │   ├── weighment/
│   │   ├── marketplace/
│   │   ├── bidding/
│   │   ├── agreement/
│   │   ├── transaction/
│   │   ├── logistics/
│   │   ├── payments/
│   │   ├── disputes/
│   │   ├── notifications/
│   │   └── audit/
│   ├── migrations/
│   └── tests/
├── packages/
├── infrastructure/
└── docs/
```

## Local backend start

1. Copy `.env.example` to `.env`.

Windows Command Prompt:

```bat
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

2. Start PostgreSQL and the API:

```bash
docker compose up --build -d
```

3. Verify the API:
- `http://localhost:8000/health`
- `http://localhost:8000/docs`

4. Run migrations:

```bash
docker compose exec api alembic upgrade head
```

5. Run backend tests:

```bash
docker compose exec api pytest
```

6. Check service status/logs if needed:

```bash
docker compose ps
docker compose logs -f api
```

## Farmer app local integration

The Farmer app automatically uses:
- Flutter Web: `http://localhost:8000/api/v1`
- Android emulator: `http://10.0.2.2:8000/api/v1`

You can override the API URL explicitly with `--dart-define=API_BASE_URL=...`.

From `apps/farmer_mobile`:

```bash
flutter pub get
flutter analyze
flutter test
flutter run -d chrome
```

Example override:

```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

For a physical Android device, use a backend address reachable from the phone (for example the development machine's LAN IP) rather than `localhost`.

The backend local configuration allows localhost/127.0.0.1 development origins on dynamic ports so Flutter Web can call the API during local testing.

## Development OTP
The development OTP provider logs/returns a predictable OTP only in local/test mode. Replace it behind `OTPProvider` before any pilot deployment.

## Important boundaries
The technical design explicitly keeps KYC/Aadhaar and payments behind provider adapters. This foundation therefore does **not** store raw Aadhaar numbers or implement a real escrow mechanism.

## TD-2 additions
See `docs/TD2_IDENTITY_LIVESTOCK.md` for implemented Farmer/Buyer profiles, individual goats, lots, localization and evidence upload contracts.

## TD-3 additions
See `docs/TD3_VERIFIED_WEIGHMENT.md` for Mandal Centre, Operator, Scale, verified weighment, acknowledgement, reweigh and QR receipt design.

## TD-4 additions
See `docs/TD4_MARKETPLACE_BIDDING.md` for listing eligibility, price recommendation metadata, search, bid idempotency, server sequencing, deterministic priority and acceptance.

## TD-5 additions
See `docs/TD5_AGREEMENT_TRANSACTION.md` for transaction creation, agreement versions, dual confirmation and authoritative state transitions.

## TD-6 additions
See `docs/TD6_FUNDS_LOGISTICS_DELIVERY.md`.

## TD-7 additions
See `docs/TD7_DISPUTES_SETTLEMENT_AUDIT.md` for disputes, controlled/independent reweigh, settlement, audit, reputation and operator scorecards.

## TD-8 additions
See `docs/TD8_HARDENING_E2E_MVP.md` and `docs/PILOT_READINESS_CHECKLIST.md`.
