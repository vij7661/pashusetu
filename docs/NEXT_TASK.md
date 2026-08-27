# PashuSetu — Current Agent Task

**Task ID:** `PILOT-GOLDENPATH-004`

**Status:** `READY`

**Work item:** Pilot Golden Path — Verified listing + quantity-first, location-prioritized Buyer marketplace + bidding + single acceptance

**Current objective:** Complete and validate the next pilot slice from an acknowledged/verified goat or lot becoming a marketplace listing through a quantity-first Buyer discovery flow that prioritizes the nearest eligible inventory, shows an estimated transportation cost and estimated landed cost for comparison, followed by multiple bids, idempotent retries, partial-lot selection with a minimum purchase of three goats, and safe acceptance, while preserving deterministic trust-layer behavior.

## Requirements authority

Follow `/AGENTS.md` and the approved SRS/MVP behavior. Preserve these product/trust rules:
- Only verified/acknowledged livestock or lot can become an active listing.
- Listing quantity/weight must use trusted verified weighment, not an unverified client-entered replacement.
- Each goat is the atomic sale unit; do not support arbitrary kilogram splitting.
- Buyer marketplace flow is **quantity first**: Buyer enters/selects the number of goats required before marketplace results/offers are displayed.
- Normal requested quantity must be at least **3 goats**.
- After quantity entry, show only currently active/available listing opportunities that can satisfy that requested quantity under the minimum-3/remaining-quantity rules.
- Eligible marketplace results must be **sorted nearest-location first by default**.
- Distance must be calculated from the Buyer's selected pickup/delivery/search location to the trusted livestock/collection/verification location used by the marketplace record; do not rank from arbitrary free-text Farmer location when a trusted verified/centre location exists.
- Show distance to the Buyer where practical (for example `12 km away`) so ranking is transparent.
- Nearest-first is the default ranking, not a hard distance filter. More distant eligible listings must still remain discoverable unless the Buyer applies an explicit distance filter later.
- Use deterministic tie-breaking when two eligible opportunities have equal/near-equal distance (for example distance first, then server-authoritative listing creation/order key), not client timestamps.
- Results should expose enough information for the Buyer to compare relevant opportunities, including distance, available goat count, trusted selected/available weight as applicable, Farmer asking/reference price where allowed, current marketplace/bid information supported by the backend, **estimated transport cost**, and **estimated landed cost**. Do not expose another Buyer's private identity or sensitive data.
- Transportation in this pilot is **estimation only**. It is not a contractual charge, not part of Farmer settlement, not collected by PashuSetu, and must not change the bid/acceptance amount.
- Label it clearly as `Estimated transport cost` and indicate that actual transportation charges may vary.
- Estimated landed cost is for Buyer comparison only: `livestock/bid value + estimated transport cost`.
- Use a simple configurable estimator, not hard-coded business logic in UI. Pilot formula should support configurable values such as `base pickup charge + (distance_km × per_km_rate) + optional load/quantity/weight adjustment`.
- Transport estimate is calculated per trip/selected purchase, not simply `number_of_goats × flat transport charge`.
- Keep estimator parameters behind development/backend configuration so pilot values can be tuned later without redesigning marketplace logic.
- Do not convert the estimate into a payment, logistics booking, guaranteed quote, settlement deduction, or Farmer liability in this task.
- For a multi-goat lot, the Buyer may bid for the requested quantity by selecting individually identifiable available goats from an eligible lot, or bid for the whole available lot.
- A partial-lot selection must contain at least 3 goats.
- A Buyer must not be allowed to submit a partial-lot bid for only 1 or 2 goats while 3+ goats are available; enforce server-side as well as in UI.
- If an available lot has fewer than 3 goats remaining, those goats may only be sold together as the complete remaining quantity; the quantity-first results may surface such a remainder only when the Buyer's requested quantity matches that complete remaining quantity.
- Quantity/location filtering is discovery convenience, not an inventory reservation. Availability must be revalidated server-side when a bid is submitted and again when an offer is accepted.
- A goat already reserved/accepted/sold in another winning selection must not be simultaneously won by another Buyer.
- Farmer may use recommended market price or own asking price only where current approved product behavior supports it; do not redesign pricing in this task.
- Buyer bids/offers must be server-authoritative.
- A client-generated idempotency key represents one user Bid intent and must be reused across HTTP retries.
- Deduplication must occur at the authoritative backend boundary before duplicate commercial effects are appended.
- Simultaneous/retried bids must not create duplicate bid intents.
- Acceptance must be concurrency-safe for the exact goat selection and prevent overlapping winners.
- Once an offer is accepted for selected goats, conflicting later accept attempts involving any of those goats must fail deterministically.
- Unselected goats remain available for later valid offers where listing state permits it.
- Audit/event history must remain sufficient to reconstruct the commercial decision path as supported by current architecture.

Do not implement real payments, escrow, external notifications, real logistics booking, settlement, disputes, or unrelated architecture in this task.

## Authorized scope

You MAY make focused changes required for this slice in:
- `apps/farmer_mobile` listing creation / offer review / acceptance flows
- `apps/buyer_mobile` quantity input / search-location input or use of stored Buyer location / marketplace results / listing detail / goat selection / bid flows
- backend marketplace / listing discovery / distance ranking / transport-estimation presentation/config / bidding / audit / related authorization endpoints, schemas, models and services where a confirmed integration defect requires it
- focused synthetic test fixtures and regression tests
- local development documentation/config where needed

Do not merge to `main`.
Do not delete databases/volumes/existing data.
Do not use real personal/payment/KYC data.

## Execute autonomously

1. At task start follow AGENTS.md: inspect working tree, `git pull --ff-only`, then re-read `AGENTS.md` and this task.
2. Verify Docker `db` and `api` health and run Alembic upgrade if needed.
3. Run baseline Flutter validation for Farmer and Buyer (`flutter pub get`, `flutter analyze`, `flutter test`).
4. Inspect current verified-weighment, marketplace/listing discovery, location fields, bidding, Farmer offer review and Buyer bidding contracts.
5. Implement/prove quantity-first, nearest-first Buyer discovery with synthetic data:
   - Buyer enters/selects required goat quantity before viewing eligible marketplace opportunities
   - use Buyer's selected/stored search location as the ranking origin
   - reject normal quantity 1 or 2
   - quantity 3+ returns only active opportunities capable of satisfying that quantity
   - stale/sold/unavailable goats are excluded
   - complete 1–2 goat remainder may be surfaced only when requested quantity exactly matches that complete remainder under the exception rule
   - eligible results are ordered by computed distance ascending by default
   - equal-distance results use deterministic server-side tie-breaking
   - more distant eligible results remain available after nearer ones; nearest-first is not a hidden hard cutoff
   - result data supports meaningful comparison including distance without leaking private Buyer information
6. Implement/prove estimation-only transport comparison:
   - calculate estimated transport from configured base charge, distance-based rate, and optional load/quantity/weight adjustment supported by a simple deterministic estimator
   - calculate estimate per trip/selection, not per-goat flat multiplication
   - expose estimated transport and estimated landed cost in Buyer marketplace/listing comparison
   - mark estimates clearly as non-binding and variable
   - confirm livestock bid/offer amount remains unchanged by transport estimate
   - confirm Farmer acceptance, transaction value, settlement/payment placeholders, and audit commercial amount do not treat estimated transport as a charge
7. Prove/implement the commercial path:
   - verified/acknowledged goat or lot → active listing with trusted market/collection location
   - Buyer selects an eligible result after quantity + availability filtering and nearest-first ranking
   - Buyer selects the requested number of individually identifiable available goats from the lot, or chooses the complete eligible lot
   - server revalidates requested quantity and selected goat availability at bid submission
   - at least two distinct Buyers can submit valid non-conflicting bids
   - total offer amount uses offer-per-kg × trusted verified weight of selected goats (or complete lot weight) where per-kg pricing applies
8. Validate idempotency: same Buyer + same idempotency key retried multiple times produces one commercial bid intent/effect; a different key is a new intent only when otherwise valid.
9. Validate server-authoritative sequencing/concurrency. Do not use client timestamps for commercial priority.
10. Validate Farmer acceptance:
   - Farmer reviews offers for own listing only
   - server revalidates selected goats at acceptance
   - accept one valid offer for a selected set
   - overlapping offers involving accepted goats cannot both win
   - non-overlapping goats remain available
   - accepted state, winning bid, selected goat IDs and remaining available IDs are persisted/retrievable
11. Preserve append-only/audit semantics supported by repository.
12. Fix only confirmed API/DTO/state/navigation/concurrency/idempotency/location-ranking/transport-estimation defects required for this slice.
13. Add/update focused automated tests covering at minimum:
   - quantity input is required before marketplace results
   - normal quantity 1 and 2 rejected
   - quantity 3+ filters out lots unable to satisfy request
   - eligible lots are returned for requested quantity
   - stale/unavailable inventory is not returned/accepted
   - complete fewer-than-3 remainder exception behaves correctly
   - nearest eligible listing is ranked first
   - distance values/ranking are computed from Buyer search location to trusted listing/collection location
   - equal-distance tie ordering is deterministic
   - farther eligible listings remain discoverable after nearer ones
   - transport estimate is deterministic for fixed config/distance/load inputs
   - changing configurable transport parameters changes only the estimate, not livestock/bid amount
   - estimated landed cost equals livestock/bid value + estimated transport
   - transport estimate is not persisted/treated as settlement/payment charge
   - unverified livestock cannot be listed
   - whole-lot bidding works
   - 1/2-goat partial bids rejected while 3+ available
   - 3-goat partial bid valid
   - multiple Buyers can bid
   - idempotent retry does not duplicate bid intent
   - unauthorized actions rejected
   - overlapping accepted offers cannot create two winners
   - unselected goats remain available after partial acceptance
14. Exercise the live local API path end-to-end with synthetic data as far as practical.
15. Re-run relevant Farmer/Buyer analyze/tests, targeted backend tests, full backend pytest if backend changed, and `/health`.
16. Inspect final diff and secret-pattern scan; remove unrelated/generated changes.
17. If all checks pass, commit/push focused changes on approved non-main branch.
18. Update/push `docs/AGENT_REPORT.md` with this exact Task ID and final status.
19. On PASS, follow AGENTS.md automatic handoff if a different READY Task ID is already published.

## Completion criteria

PASS requires actual proof that:
- Buyer must enter/select quantity before marketplace opportunities are displayed
- normal requested quantity is minimum 3 goats
- marketplace results are filtered to currently eligible inventory for that quantity
- eligible results are sorted nearest-first by default using Buyer search location and trusted inventory/collection location
- distance is visible/available to the Buyer where practical
- nearest-first does not hide more distant eligible opportunities
- deterministic tie-breaking exists for equal/near-equal distance
- estimated transportation cost and estimated landed cost are shown for Buyer comparison
- transportation remains estimation-only and does not alter bid amount, Farmer acceptance amount, payment/settlement, or transaction value
- estimator uses configurable deterministic parameters rather than hard-coded UI values
- quantity/location filtering does not falsely reserve inventory; server revalidates at bid and acceptance
- whole-lot and valid partial-lot bidding are supported
- complete 1–2 goat remainder exception is handled without stranding inventory
- arbitrary kg splitting is not supported
- multiple Buyers can bid safely
- same idempotency key does not duplicate commercial effects
- server authority determines sequencing
- no goat can belong to two accepted offers
- unselected goats remain available after valid partial acceptance
- affected Flutter analyze/tests and backend tests pass
- local API health remains good
- no prohibited/destructive action occurred

GUI-only presentation may remain for consolidated human QA later; clearly separate automated proof from pending visual QA.

## Completion report

Report Task ID/status, root causes/gaps, Farmer and Buyer validation, exact quantity-first + nearest-first discovery and bidding flow exercised, minimum-3/remainder behavior, distance-ranking/tie-break results, transport-estimator config/formula and non-binding/settlement-separation proof, idempotency/concurrency/authorization/audit results, backend test results, files changed, branch/commit SHAs, remaining manual QA, working tree state, and safety confirmation.
