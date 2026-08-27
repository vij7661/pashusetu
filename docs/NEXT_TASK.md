# PashuSetu — Current Agent Task

**Task ID:** `PILOT-GOLDENPATH-004`

**Status:** `READY`

**Work item:** Pilot Golden Path — Verified listing + quantity-first, nearest-first Buyer marketplace + bidding + single acceptance

**Current objective:** Resume and complete the marketplace slice after resolving the trust/business blockers reported by Codex. Preserve all previously validated non-ambiguous behavior and implement the explicit decisions below.

## Requirements authority

Follow `/AGENTS.md` and the approved SRS/MVP behavior.

## Explicit blocker resolutions — APPROVED

1. **Trusted weight for partial-lot purchases**
   - Partial-lot bidding is allowed only when every individually selectable goat has its own trusted verified weight captured during the Operator verification process and linked to that Goat ID.
   - Do **not** estimate a selected goat's weight by equal division of a whole-lot weight.
   - Do **not** allocate lot weight proportionally or invent any other derived weight rule.
   - A lot with only one aggregate locked weight and no trusted per-goat verified weights is **whole-lot-only** for the pilot.
   - For a valid partial selection, commercial weight is the sum of the selected goats' trusted verified weights.
   - Offer total where per-kg pricing applies = `offer_per_kg × sum(selected trusted goat weights)`.

2. **Authoritative distance/location model**
   - Add/store trusted `latitude` and `longitude` for `MandalCentre`/verified collection location as the authoritative marketplace location.
   - Buyer search origin is the Buyer's stored coordinates or an explicitly selected search/pickup/delivery coordinate.
   - Nearest-first ranking must use Buyer search coordinates → trusted Centre/collection coordinates.
   - Do not rank from Farmer free-text address when trusted Centre coordinates exist.
   - If a listing lacks trusted coordinates, it may remain discoverable only after coordinate-capable listings and must be clearly treated as distance unavailable; do not fabricate coordinates.

3. **Minimum quantity / remainder rule**
   - The pilot minimum purchase from a lot is a strict **3 goats**.
   - Remove the previously proposed 1–2 goat remainder exception.
   - Buyer quantity input of 1 or 2 is rejected.
   - A partial bid selecting 1 or 2 goats is rejected.
   - If only 1 or 2 goats remain after prior accepted sales, those goats are not independently purchasable through this listing in the pilot.
   - The Farmer may later combine/relist those remaining goats with other verified goats so a new eligible lot contains at least 3 goats.
   - Do not create an alternate remainder-mode API/UX in this task.

4. **Identifiable inventory completeness**
   - Partial-lot eligibility requires every declared animal in the lot to have an individual Goat ID/link.
   - A lot where `declared_quantity` exceeds the number of linked identifiable goats is **not eligible for partial-lot bidding**.
   - Such an incomplete lot may be whole-lot-only only if the existing verified aggregate-lot contract safely supports it; otherwise keep it ineligible until inventory identity is complete.
   - Never create synthetic Goat IDs merely to satisfy declared quantity.

## Existing approved marketplace rules

- Only verified/acknowledged livestock/lot can become an active listing.
- Buyer flow is quantity first; normal requested quantity minimum is 3 goats.
- Eligible results are nearest-first by default, not a hard distance cutoff.
- Show distance where available, available quantity, trusted verified weight, allowed asking/reference price/bid information, estimated transport, and estimated landed cost without exposing another Buyer's private identity.
- Transportation is estimation-only and must not change bid amount, Farmer acceptance amount, transaction value, settlement or payment.
- Transport estimator must be configurable and deterministic, e.g. base pickup + distance component + optional load/weight adjustment, calculated per trip/selection.
- Quantity/location search is not an inventory reservation; availability must be revalidated at bid submission and acceptance.
- Same Buyer + same idempotency key must create one commercial bid intent/effect.
- Server authority determines sequencing; do not use client timestamps for priority.
- Overlapping accepted selections cannot result in the same goat being won twice.
- Unselected goats remain available while they still satisfy listing/inventory rules.
- Append-only/audit history must preserve the commercial decision path supported by the repository.

Do not implement real payments, escrow, external notifications, real logistics booking, settlement, disputes, or unrelated architecture in this task.

## Authorized scope

You MAY make focused changes in:
- `apps/farmer_mobile` listing / offer review / acceptance
- `apps/buyer_mobile` quantity input / location / results / goat selection / bidding
- `apps/operator_mobile` only where needed to capture/display trusted per-goat verified weights for partial-lot eligibility
- backend livestock/weighment/identity/centre/marketplace/bidding/audit models, migrations, schemas, services and routes required for these approved decisions
- focused tests and synthetic fixtures

Non-destructive schema migrations required for trusted Centre coordinates or trusted per-goat verified weight support are authorized under AGENTS.md. Do not delete/reset existing data.

## Execute autonomously

1. Follow AGENTS.md task start: inspect working tree, `git pull --ff-only`, re-read AGENTS.md and this task.
2. Preserve and build on partial implementation commit `98e7b046bd1b9ff39f6d7c6feddec682612339db`; do not undo already validated privacy/idempotency/audit/acceptance fixes unless a test proves they are wrong.
3. Verify Docker `db`/`api`, Compose, Alembic, and `/health`.
4. Run Farmer, Buyer, and Operator baseline validation where affected.
5. Implement/prove trusted per-goat verification support needed for partial-lot selection. Whole-lot-only fallback must remain explicit when per-goat trusted weights are unavailable.
6. Implement/prove trusted Centre coordinates and nearest-first distance ranking.
7. Implement strict minimum-3 behavior with no 1–2 remainder exception.
8. Implement/prove partial-lot eligibility requires complete Goat-ID linkage and trusted per-goat verified weights.
9. Implement/prove quantity-first marketplace filtering and nearest-first ordering.
10. Implement/prove estimation-only transport and landed-cost presentation; commercial transaction amounts must remain unchanged.
11. Validate bid idempotency, server sequencing, privacy/authorization, overlap prevention and single-winner acceptance.
12. Add focused tests at minimum for:
   - aggregate-weight-only lot is whole-lot-only
   - selected partial-lot commercial weight equals sum of trusted selected Goat weights
   - no equal-division/derived selected weight fallback exists
   - Centre coordinate distance ranking works and nearest eligible result is first
   - missing trusted listing coordinates do not cause fabricated distance
   - quantity 1 and 2 rejected
   - partial bid of 1 or 2 rejected
   - 1–2 goats remaining are not purchasable through the same listing
   - incomplete `declared_quantity` vs Goat-link inventory cannot be partial-bid
   - fully linked/verified 3+ goat selection can bid
   - whole-lot path remains valid where supported
   - transport estimate is deterministic/configurable and does not alter commercial amount
   - same idempotency key does not duplicate bid intent
   - overlapping accepted selections cannot produce duplicate winners
   - authorization/privacy/audit behavior from the validated partial implementation remains covered
13. Exercise the live local API path with synthetic data as practical.
14. Re-run relevant Flutter analyze/tests, targeted backend tests, full backend pytest after backend/schema changes, migrations, and `/health`.
15. Inspect diff, migration safety, and secret-pattern scan; remove unrelated changes.
16. If all checks pass, commit and push focused changes on the approved non-main branch.
17. Update and push `docs/AGENT_REPORT.md` with this exact Task ID and final status.
18. On PASS, follow AGENTS.md automatic handoff only if a different READY Task ID is already published.

## Completion criteria

PASS requires actual proof of the explicit blocker resolutions above plus the previously approved marketplace/idempotency/acceptance behavior. GUI-only presentation may remain for consolidated human QA; distinguish it clearly from automated proof.

## Completion report

Report Task ID/status; all four blocker resolutions; Farmer/Buyer/Operator validation; quantity-first + nearest-first discovery; trusted per-goat weight behavior; strict minimum-3 behavior; Centre-coordinate model; transport estimate separation; idempotency/concurrency/authorization/audit results; migrations; backend tests; files changed; branch/commit SHAs; manual QA; working tree; safety confirmation.
