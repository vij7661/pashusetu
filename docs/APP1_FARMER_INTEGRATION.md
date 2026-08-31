# APP-1 — Farmer Application Integration

The Farmer mobile client has now moved from static HTML prototype to a Flutter application using the actual TD-8 API surface.

## Key principle
The mobile app does not own commercial truth. Weight, bid sequence, accepted offer, agreement state and transaction state come from the backend.

For pilot agreements, the Farmer app submits only transaction-specific inputs that the Farmer can actually provide: pickup point, final weighing point and allowed tolerance. Platform business terms such as price basis, transport responsibility and dispute handling are owned by the backend contract. The mobile client must not hard-code or override them. After agreement creation, the app renders the terms returned by the server.

The Farmer app must also never prefill fabricated operational facts such as a mandal centre, buyer scale identifier, verified weight, market price or transaction tolerance. Those values must come from the relevant authoritative service or explicit Farmer/operator input.

Settlement display is read-only in the Farmer app. Viewing or refreshing settlement details must call the settlement GET endpoint and must never create a settlement as a side effect. Settlement creation remains a distinct backend mutation with transaction-state enforcement.

Final transaction closure is backend/system-owned after settlement finality. The Farmer app has no close mutation and cannot trigger reputation processing by client action.

Dispute parties may open a dispute and submit evidence, but they do not own the final resolution. Final decision, resolution rule and settlement adjustment are platform-controlled and require an authorized Admin or Operator resolver in the pilot. Reweigh evidence must be verified and must match the exact goat/lot and Farmer identity from the disputed listing; an unrelated verified weighment cannot be attached to the case. Additional evidence or reweighs are rejected after the dispute is resolved.

Shipment UI must not infer that pickup, transit, delivery, weighment or evidence milestones happened merely because those steps exist in the workflow. Until verified event data is returned by the backend, the Farmer app shows only the authoritative transaction state.

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
| Settlement status | `GET /payments/transactions/{id}/settlement` |
| Open dispute | `POST /disputes/transactions/{id}` |
| Dispute evidence/reweigh | `POST /disputes/{id}/evidence`, `POST /disputes/{id}/reweigh` |

There is intentionally no Farmer-facing transaction-close or dispute-resolution endpoint.

## Remaining provider-dependent UI
- Aadhaar/KYC verification
- payout/bank/UPI provider integration
- object-storage upload execution
- SMS/WhatsApp/push notifications

These are intentionally left behind adapters instead of being mocked as production functionality.
