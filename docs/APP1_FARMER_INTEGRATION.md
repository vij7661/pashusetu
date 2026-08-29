# APP-1 — Farmer Application Integration

The Farmer mobile client has now moved from static HTML prototype to a Flutter application using the actual TD-8 API surface.

## Key principle
The mobile app does not own commercial truth. Weight, bid sequence, accepted offer, agreement state and transaction state come from the backend.

For pilot agreements, the Farmer app submits only transaction-specific inputs that the Farmer can actually provide: pickup point, final weighing point and allowed tolerance. Platform business terms such as price basis, transport responsibility and dispute handling are owned by the backend contract. The mobile client must not hard-code or override them. After agreement creation, the app renders the terms returned by the server.

The Farmer app must also never prefill fabricated operational facts such as a mandal centre, buyer scale identifier, verified weight, market price or transaction tolerance. Those values must come from the relevant authoritative service or explicit Farmer/operator input.

## Implemented connection map

| Farmer UI | Backend |
|---|---|
| Existing login | `POST /auth/otp/request`, `POST /auth/otp/verify` |
| Profile | `GET /identity/farmers/me` |
| New farmer profile | `POST /identity/farmers` |
| Individual goat | `POST /livestock/goats` |
| Lot | `POST /livestock/lots` |
| Evidence contract | `POST /livestock/evidence/upload-contract` |
| Market recommendation | `GET /marketplace/recommendations` |
| Publish listing | `POST /marketplace/listings` |
| Offers | `GET /bidding/listings/{id}/bids` |
| Accept offer | `POST /bidding/listings/{id}/accept/{bid}` |
| Transaction | `GET /transaction/{id}` |
| Agreement | `/agreement/transactions/*` |
| Dispute | `/disputes/transactions/*` |

## Remaining provider-dependent UI
- Aadhaar/KYC verification
- payout/bank/UPI provider integration
- object-storage upload execution
- SMS/WhatsApp/push notifications

These are intentionally left behind adapters instead of being mocked as production functionality.
