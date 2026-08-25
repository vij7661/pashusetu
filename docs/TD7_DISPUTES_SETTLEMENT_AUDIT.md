# TD-7 — Disputes, Settlement & Audit

## Implemented
- dispute entity
- disputed amount
- evidence references
- controlled reweigh attachment
- independent verified-scale reweigh attachment
- resolution rule
- final decision
- settlement adjustment
- final settlement record
- configurable platform-fee basis points
- append-only transaction audit events
- ordered event retrieval
- Farmer / Buyer reputation records
- Operator scorecard records

## Dispute flow
```text
TOLERANCE_CHECK
→ DISPUTED
→ open dispute
→ freeze disputed amount at provider/operations layer
→ evidence review
→ controlled reweigh
→ if unresolved: independent verified scale
→ resolution rule applied
→ RESOLVED
→ settlement adjustment
→ SETTLED
→ CLOSED
```

## Evidence model
A dispute can reference:
- origin weighment
- delivery weighment
- Scale IDs
- server timestamps
- origin verification video
- pickup video
- delivery video
- Goat / Lot IDs
- agreement version and tolerance terms
- controlled / independent reweigh sessions

## Audit
The audit log is append-only by convention and is ordered per aggregate using an authoritative sequence.
Important production commands should call `append_event()`.

Current TD-7 explicitly emits:
- `DISPUTE_OPENED`
- `DISPUTE_RESOLVED`
- `SETTLEMENT_COMPLETED`

Earlier modules should be progressively upgraded to emit their own domain events in the hardening phase.

## Settlement
Settlement begins with the accepted bid gross amount and applies:
- dispute adjustment
- platform fee

The current default example uses 150 basis points = 1.5%.

This is configurable code, not a final commercial/legal decision.

## Reputation
Initial model tracks:
- completed transactions
- disputes
- lost disputes
- simple score

Operator scorecards track:
- weighment count
- reweigh count
- dispute-linked count

These signals must not be treated as automatic fraud verdicts.

## Production hardening still required
- true disputed-funds hold/release through selected payment provider
- signed admin decision authority
- role restrictions for dispute resolution
- immutable event enforcement at DB/infrastructure level
- event outbox for notifications/analytics
- full replay projector
- dispute SLA/escalation timers
- farmer/buyer rating input model
- appeal policy if product/legal design requires one
- score normalization based on volume/context

## Next: TD-8 Hardening & End-to-End MVP
- complete audit events across all modules
- idempotency on all critical mutations
- security tightening / RBAC
- integration tests with PostgreSQL
- concurrent bid tests
- full E2E Farmer→Operator→Buyer→Delivery→Settlement/Dispute
- object storage adapter
- notification adapter
- seed/demo data
- OpenAPI export
- CI pipeline
