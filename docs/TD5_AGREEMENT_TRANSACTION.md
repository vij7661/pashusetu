# TD-5 — Agreement & Transaction

## Implemented
- Transaction created from the accepted bid
- Exactly one transaction per accepted listing
- Farmer / Buyer party ownership
- Authoritative transaction state machine
- Agreement proposal
- Agreement version number
- Price basis
- Pickup point
- Final weighing point
- Weight tolerance
- Transport responsibility
- Dispute rule
- Farmer confirmation
- Buyer confirmation
- Agreement locks only after both parties confirm
- Active agreement attached to the transaction
- Invalid transaction-state jumps rejected

## Approved flow
```text
OFFER_ACCEPTED
→ AGREEMENT_PENDING
→ AGREEMENT_LOCKED
→ FUNDS_SECURED
→ PICKUP_SCHEDULED
→ PICKED_UP
→ IN_TRANSIT
→ DELIVERED
→ DELIVERY_VERIFICATION
→ TOLERANCE_CHECK
→ SETTLED or DISPUTED
→ RESOLVED
→ SETTLED
→ CLOSED
```

## Agreement immutability
The currently locked agreement is treated as a contract snapshot.

If the product later permits changes:
- do not edit a locked row silently
- create a new agreement version
- require both parties to confirm the new version
- append an audit event showing which version became active

## Tolerance
Tolerance is persisted as basis points.

Example:
- 1.5% = 150 basis points

This avoids floating-point storage for contract rules.

## Dual confirmation
Farmer and Buyer must both confirm the **same Agreement ID/version**.

A transaction cannot enter `AGREEMENT_LOCKED` until both confirmations exist.

## Important production hardening still required
- automatic AuditEvent emission around transaction/agreement commands
- idempotency on agreement creation/confirmation
- explicit rejection / counter-proposal workflow
- agreement expiry rules
- legal text/version references
- terms acceptance timestamp and device/request metadata
- admin support actions with audit controls
- concurrency test with two simultaneous confirmation requests

## Next slice: TD-6 Funds, Logistics & Delivery
- payment/secured-funds provider adapter
- payment intents and callbacks
- transporter assignment
- pickup QR verification
- goat count / loading video / departure
- delivery QR verification
- delivery weighment linkage
- tolerance calculation
- settlement or dispute routing
