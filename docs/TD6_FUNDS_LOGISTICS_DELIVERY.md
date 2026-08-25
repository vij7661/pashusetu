# TD-6 — Funds, Logistics & Delivery

Implemented:
- payment/secured-funds provider abstraction
- simulated provider for development
- payment intent persistence
- provider webhook-event persistence model
- transporter/driver/vehicle assignment
- pickup QR requirement
- pickup goat count
- loading video evidence reference
- departure record
- in-transit state
- delivery QR requirement
- verified delivery weighment linkage
- delivery evidence reference
- contractual tolerance calculation
- automatic settlement vs dispute routing

## Flow
AGREEMENT_LOCKED → FUNDS_SECURED → PICKUP_SCHEDULED → PICKED_UP → IN_TRANSIT
→ DELIVERED → DELIVERY_VERIFICATION → TOLERANCE_CHECK
→ SETTLED (within tolerance) OR DISPUTED (outside tolerance)

## Important
The included funds provider is simulated. No real payment provider, escrow product, or regulatory assumption is hard-coded.
A production provider must replace the adapter after commercial/compliance selection.

## Next: TD-7 Disputes, Settlement & Audit
Controlled reweigh, independent scale, evidence review, disputed-amount freeze,
resolution, settlement adjustment, append-only domain events, operator scorecard and reputation.
