# APP-1 — Farmer Application Integration

The Farmer mobile client has now moved from static HTML prototype to a Flutter application using the actual TD-8 API surface.

## Key principle
The mobile app does not own commercial truth. Weight, bid sequence, accepted offer, agreement state and transaction state come from the backend.

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
