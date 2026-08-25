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

## Local start

1. Copy `.env.example` to `.env`.
2. Run:

```bash
docker compose up --build
```

3. API:
- `http://localhost:8000/health`
- `http://localhost:8000/docs`

4. Run migrations:

```bash
docker compose exec api alembic upgrade head
```

5. Run tests:

```bash
docker compose exec api pytest
```

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
