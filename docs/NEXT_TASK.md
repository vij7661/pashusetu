# PashuSetu — Current Agent Task

**Task ID:** `PILOT-GOLDENPATH-004`

**Status:** `READY`

**Work item:** Pilot Golden Path — Verified listing + Buyer marketplace + bidding + single acceptance

**Current objective:** Complete and validate the next pilot slice from an acknowledged/verified goat or lot becoming a marketplace listing through Buyer discovery, multiple bids, idempotent retries, partial-lot selection with a minimum purchase of three goats, and exactly one accepted offer, while preserving deterministic trust-layer behavior.

## Requirements authority

Follow `/AGENTS.md` and the approved SRS/MVP behavior. Preserve these trust rules:
- Only verified/acknowledged livestock or lot can become an active listing.
- Listing quantity/weight must use the trusted verified weighment, not an unverified client-entered replacement.
- Each goat is the atomic sale unit; do not support arbitrary kilogram splitting of a goat/lot.
- For a multi-goat lot, a Buyer may bid/purchase the whole available lot or select individual available goats, but a partial-lot selection must contain at least **3 goats**.
- A Buyer must not be allowed to submit a partial-lot bid for only 1 or 2 goats. Enforce this server-side; client validation alone is insufficient.
- If an available lot has fewer than 3 goats remaining, the remaining goats may only be sold together as the complete remaining quantity; do not strand 1–2 goats because of the minimum rule.
- A goat already reserved/accepted/sold in another winning selection must not be simultaneously won by another Buyer.
- Farmer may use recommended market price or own asking price only where current approved product behavior supports it; do not redesign pricing in this task.
- Buyer bids/offers must be server-authoritative.
- A client-generated idempotency key represents one user Bid intent and must be reused across HTTP retries.
- Deduplication must occur at the authoritative backend boundary before duplicate commercial effects are appended.
- Simultaneous/retried bids must not create duplicate bid intents.
- Acceptance must be concurrency-safe for the exact goat selection and must prevent overlapping winners.
- Once an offer is accepted for selected goats, conflicting later accept attempts involving any of those goats must fail deterministically and must not silently overwrite accepted state.
- Unselected goats remain available for later valid offers where the listing state permits it.
- Audit/event history must remain sufficient to reconstruct the commercial decision path as supported by the current architecture.

Do not implement real payments, escrow, external notifications, logistics, settlement, disputes, or unrelated architecture in this task.

## Authorized scope

You MAY make focused changes required for this slice in:
- `apps/farmer_mobile` listing creation / offer review / acceptance flows
- `apps/buyer_mobile` marketplace / listing detail / goat selection / bid flows
- backend marketplace / bidding / audit / related authorization endpoints, schemas, models and services where a confirmed integration defect requires it
- focused synthetic test fixtures and regression tests
- local development documentation/config where needed

Do not merge to `main`.
Do not delete databases/volumes/existing data.
Do not use real personal/payment/KYC data.

## Execute autonomously

1. At task start follow AGENTS.md: inspect working tree, `git pull --ff-only`, then re-read `AGENTS.md` and this task.
2. Verify Docker `db` and `api` health and run Alembic upgrade if needed.
3. Run baseline Flutter validation:
   - Farmer: `flutter pub get`, `flutter analyze`, `flutter test`
   - Buyer: `flutter pub get`, `flutter analyze`, `flutter test`
4. Inspect current verified-weighment, marketplace, bidding, Farmer offer review and Buyer bidding contracts.
5. Using safe synthetic data, prove or implement the path:
   - verified/acknowledged goat or lot → active listing
   - Buyer discovery/listing retrieval
   - whole-lot bid or selection of individually identifiable available goats from a lot
   - reject partial selection of 1 or 2 goats when 3+ goats are available
   - accept partial selection of 3+ goats
   - when fewer than 3 goats remain available, allow only purchase of the complete remaining quantity
   - at least two distinct Buyers can submit valid non-conflicting bids
   - total offer amount shown/calculated from offer-per-kg × trusted verified weight of the selected goats (or complete lot weight for whole-lot offer) where current product flow uses per-kg pricing
6. Validate idempotency behavior:
   - same Buyer + same idempotency key retried multiple times produces one commercial bid intent/effect
   - duplicate transmission does not append duplicate authoritative bid records/events
   - different idempotency key represents a new intent only when otherwise valid
7. Validate ordering/concurrency behavior using server-authoritative sequencing/timestamps already modeled by the backend. Do not use client timestamps for commercial priority.
8. Validate Farmer acceptance:
   - Farmer can review offers for own listing only
   - accept one valid offer for a selected set of goats
   - overlapping offers involving any already accepted goat cannot both win
   - non-overlapping valid selections may remain available/eligible according to listing state
   - repeated/concurrent acceptance attempts for overlapping selections fail cleanly/deterministically
   - accepted state, winning bid, selected goat IDs and remaining available goat IDs are persisted/retrievable
9. Preserve append-only/audit semantics supported by the repository; add focused coverage if current code lacks proof of the bid/acceptance decision history.
10. Fix only confirmed API/DTO/state/navigation/concurrency/idempotency defects required for this approved slice. Do not weaken authorization or determinism to make tests pass.
11. Add or update focused automated tests covering at minimum:
   - unverified livestock cannot be listed
   - verified livestock/lot listing succeeds
   - whole-lot bidding works
   - 1-goat and 2-goat partial-lot bids are rejected when 3+ are available
   - 3-goat partial-lot bid is accepted as a valid bid intent
   - fewer-than-3 remaining goats can be purchased only as the complete remaining quantity
   - multiple Buyers can bid
   - idempotent retry does not duplicate a bid intent
   - unauthorized Buyer/Farmer actions are rejected
   - overlapping accepted offers cannot create two winners for the same goat
   - unselected goats remain available after a partial acceptance
12. Exercise the live local API path end-to-end with synthetic data as far as practical.
13. Re-run relevant validation:
   - Farmer analyze/tests if changed
   - Buyer analyze/tests if changed
   - targeted backend tests
   - full backend pytest suite if backend code changes
   - `/health`
14. Inspect the final diff, secret-pattern scan, and remove unrelated/generated changes.
15. If all relevant checks pass, commit and push focused implementation changes on the approved non-main branch.
16. Update and push `docs/AGENT_REPORT.md` with this exact Task ID and final status.
17. If status is `PASS`, follow the AGENTS.md automatic task handoff rule and execute a different READY Task ID if one is already published.

## Completion criteria

This task is `PASS` only when actual checks/tests support:
- only verified/acknowledged livestock/lot can become an active listing
- Buyer marketplace can retrieve the active listing and individually identifiable goats within a lot as needed for selection
- whole-lot purchase/bidding is supported
- partial-lot purchase/bidding requires at least 3 goats while 3+ remain available
- if only 1 or 2 goats remain, they can be purchased only together as the complete remaining quantity
- arbitrary kg splitting is not supported
- multiple Buyers can place valid bids
- retrying the same Bid intent with the same idempotency key does not create duplicate commercial effects
- server authority, not client timestamp, determines commercial sequencing where applicable
- Farmer can review and accept only offers on own listing
- no goat can belong to two accepted/winning offers
- unselected goats remain available after a valid partial acceptance
- affected Flutter analyze/tests pass
- relevant backend tests pass and local API health remains good
- no prohibited/destructive action occurred

GUI-only presentation may remain for consolidated human QA later; clearly separate automated proof from pending visual QA.

## Completion report

Report:
- Task ID and final status
- root causes/gaps found
- Farmer analyze/test results
- Buyer analyze/test results
- exact listing/selection/bidding/acceptance flow exercised
- minimum-3 and remaining-quantity rule results
- idempotency/concurrency results
- authorization/audit results
- backend targeted/full-suite results
- files changed
- branch and implementation commit SHA(s)
- remaining manual QA items
- working tree state
- safety confirmation
