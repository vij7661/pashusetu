# TD-4 — Marketplace & Bidding

## Implemented
- Verified-listing eligibility
- Market-price recommendation metadata
- Farmer price per kg
- Farmer total listing-value calculation
- Listing open/close timestamps
- Buyer search by weight range
- Bid price per kg
- Automatic buyer total-offer calculation
- Durable idempotency records in PostgreSQL
- One bid intent = one idempotency key
- Server-authoritative sequence per listing
- Duplicate retry returns original bid
- Late bid after close is rejected
- Deterministic bid acceptance
- Equal-price tie: earliest server sequence wins
- Farmer can accept exactly one highest-priority valid offer

## Price calculation
All money uses integer paise.

Example:
- verified weight = 50.000 kg
- farmer price = ₹400/kg = 40,000 paise/kg
- total = ₹20,000 = 2,000,000 paise

Buyer example:
- 50.000 kg × ₹492/kg
- total offer = ₹24,600

## Recommendation
`MarketPriceRecommendation` is informational metadata.
The farmer may use it or enter their own price.

The recommendation source itself is not implemented here because the final provider/data source is still an open business decision.

## Bidding priority
Priority is deterministic:
1. Higher valid ₹/kg price first.
2. For equal prices, lower/earlier authoritative server sequence wins.

Client device timestamps are not used for ordering.

## Idempotency
A mobile client should create the idempotency key when the buyer taps **Bid**, not per HTTP retry.

Retry:
```text
same buyer + same idempotency key + same request
→ same Bid ID + same server sequence + same status
```

Reuse of the same key with a different bid payload returns an error.

## Concurrency
Listing rows and sequence rows are locked in PostgreSQL before:
- assigning a bid sequence
- accepting the winning bid

This is the MVP approach to avoid Redis-only correctness.

## Important hardening still required
- audit-event emission for every bid/listing command
- explicit listing version / optimistic concurrency on farmer edits
- minimum bid increment rules if product decides to use them
- farmer cancellation policy
- bid withdrawal policy
- scheduled close worker/automation
- marketplace geospatial search
- buyer/farmer reputation filters
- performance and race-condition tests against PostgreSQL

## Next slice: TD-5 Agreement & Transaction
- transaction creation from accepted bid
- immutable agreement version
- dual party confirmation
- price basis / pickup / final weighing point / tolerance
- transport responsibility
- dispute rule
- authoritative transaction state transitions
