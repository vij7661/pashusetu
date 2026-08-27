# PashuSetu — Current Agent Task

**Task ID:** `PILOT-GOLDENPATH-005`

**Status:** `READY`

**Work item:** Pilot Golden Path — Accepted offer → agreement snapshot → pickup/delivery evidence → tolerance → settlement/dispute routing

**Current objective:** Extend the validated marketplace flow from an accepted Bid/Transaction into an immutable agreement snapshot, controlled pickup/delivery evidence, trusted delivery weighment comparison, deterministic tolerance evaluation, and routing to settlement-ready or dispute-required state. Keep real payment execution out of scope.

## Requirements authority

Follow `/AGENTS.md` and the approved SRS/MVP behavior. Build on the validated `PILOT-GOLDENPATH-004` implementation; do not redesign marketplace/bidding rules.

## Trust/business rules

- An accepted Bid is the authoritative commercial source for creating the transaction/agreement.
- Create/store an immutable or versioned **agreement snapshot** containing at minimum the accepted Bid ID, Farmer, Buyer, listing, selected Goat IDs/whole-lot intent, accepted price-per-kg, trusted agreed weight, commercial livestock amount, and relevant server-authoritative timestamps/identifiers.
- Transport estimate from marketplace discovery is informational only and must not become part of the agreement commercial amount, settlement amount, or payment obligation.
- Do not silently mutate a locked agreement. Corrections require an explicit version/superseding record or approved state transition supported by the architecture.
- Pickup/delivery evidence must be attributable to the transaction and actor, timestamped server-side, and auditable. Use synthetic/local evidence references in automated tests; do not integrate paid/external storage in this patch.
- Delivery/final weighment used for tolerance must be a trusted Operator/approved verification reading. Do not use arbitrary Buyer/Farmer-entered weight as settlement authority.
- Never overwrite the original agreed/verified weighment when recording delivery/final weighment.
- Tolerance must be deterministic and backend-authoritative. Reuse the repository/SRS tolerance rule if already defined. If no approved numeric tolerance threshold exists, STOP and report the missing business decision rather than inventing a percentage.
- Tolerance comparison must use the same commercial selection scope: selected Goat IDs for partial transactions or whole-lot scope for whole-lot transactions.
- If delivery weight is within the approved tolerance, route transaction to a **settlement-ready / no-dispute-required** state supported by the existing state model.
- If outside tolerance, route to **dispute-required/open-dispute** path; do not auto-settle.
- A dispute must preserve the agreement snapshot, original trusted weight, delivery trusted weight, variance/tolerance result, evidence references and audit history.
- State transitions must be idempotent/concurrency-safe: repeated evidence/finalization requests must not create duplicate commercial effects, duplicate disputes or contradictory terminal states.
- Authorization must ensure Farmer/Buyer/Operator/Admin can only perform actions permitted by their role and transaction relationship.
- Keep append-only/audit reconstruction sufficient to explain who did what, when, against which agreement/evidence/weight.

Do not implement real payment capture, escrow, bank/UPI transfer, refunds, real logistics booking, real SMS/WhatsApp, paid evidence storage, or production deployment in this task.

## Authorized scope

Focused changes are allowed in:
- backend transaction/agreement, evidence, weighment/tolerance, dispute, settlement-status and audit models/schemas/services/routes
- non-destructive Alembic migrations required for the approved snapshot/evidence/state model
- `apps/farmer_mobile` transaction/agreement/status/dispute presentation required for this slice
- `apps/buyer_mobile` transaction/agreement/evidence/status presentation required for this slice
- `apps/operator_mobile` pickup/delivery verification/evidence/final weighment workflow required for this slice
- focused synthetic fixtures and automated regression tests

Do not merge to `main`, delete/reset databases/volumes, or use real personal/KYC/payment data.

## Execute autonomously

1. Follow AGENTS.md task start: inspect working tree, `git pull --ff-only`, then re-read AGENTS.md and this task.
2. Verify Docker Compose, PostgreSQL/API health, Alembic head and `/health`.
3. Run baseline Farmer, Buyer and Operator Flutter validation where affected.
4. Inspect existing Transaction, Dispute, settlement status, weighment and audit contracts before changing schema/state behavior.
5. Confirm whether the repository/SRS already defines the numeric tolerance threshold/formula. If it is absent or contradictory, publish `BLOCKED` with the exact missing decision and stop before inventing one.
6. Implement/prove agreement snapshot creation from accepted Bid/Transaction. Snapshot commercial fields must be derived from authoritative accepted state, not resubmitted client values.
7. Implement/prove transaction-scoped pickup/delivery evidence using safe local/synthetic evidence references and server-side metadata/audit records.
8. Implement/prove trusted delivery/final weighment without overwriting original trusted agreement/weighment history.
9. Implement/prove deterministic tolerance calculation using the approved existing rule and exact transaction selection scope.
10. Implement/prove routing:
   - within tolerance → settlement-ready/no-dispute-required
   - outside tolerance → dispute-required/open dispute
   - no real payment movement occurs
11. Validate idempotency/concurrency so retries cannot duplicate agreement snapshots, evidence effects, finalization, disputes or settlement-ready transitions.
12. Validate role/ownership authorization and prevent unrelated Farmer/Buyer access/actions.
13. Preserve/extend append-only audit history for agreement creation, evidence, final weighment, tolerance decision and dispute/settlement routing.
14. Add focused automated tests at minimum for:
   - accepted Bid creates authoritative agreement snapshot
   - client cannot alter accepted price/weight/selected Goat IDs through snapshot/finalization payload
   - transport estimate is absent from commercial agreement/settlement amount
   - agreement cannot be silently mutated after lock
   - pickup/delivery evidence is transaction-scoped and auditable
   - untrusted client-entered final weight cannot determine settlement
   - original trusted weight remains preserved after delivery weighment
   - within-tolerance route reaches settlement-ready state
   - outside-tolerance route opens/routes to dispute and does not settlement-ready
   - repeated same finalization/evidence intent is idempotent
   - concurrent/repeated finalization cannot create contradictory states or duplicate disputes
   - unauthorized/unrelated actors are rejected
   - partial-lot tolerance uses exactly the selected Goat scope
15. Exercise the live local API path end-to-end with synthetic data as practical: accepted marketplace offer → agreement → evidence → trusted final weighment → tolerance → route.
16. Re-run affected Flutter `flutter pub get`, `flutter analyze`, `flutter test`; targeted backend tests; full backend pytest after backend/schema changes; migrations; `/health`.
17. Inspect final diff, migration safety and secret-pattern scan; revert unrelated/generated changes.
18. If all checks pass, commit and push focused implementation on the approved non-main branch.
19. Update and push `docs/AGENT_REPORT.md` with this exact Task ID and final status.
20. On PASS, follow AGENTS.md automatic handoff only if a different READY Task ID is already published.

## Completion criteria

PASS requires automated/live-local proof that an accepted offer becomes an authoritative immutable/versioned agreement; transaction evidence and trusted final weighment are preserved/auditable; the approved tolerance rule deterministically routes within-tolerance transactions to settlement-ready and outside-tolerance transactions to dispute; retries/concurrency do not create duplicate or contradictory commercial effects; authorization holds; transport estimate remains informational; affected Flutter/backend tests pass; local API/database/migrations remain healthy; and no prohibited/destructive action occurred.

GUI-only presentation may remain for consolidated human QA later; distinguish automated proof from pending visual QA.

## Completion report

Report Task ID/status; tolerance rule actually used and its source in repository/SRS; agreement snapshot fields/immutability proof; evidence/final-weighment flow; within/outside tolerance results; settlement/dispute routing; idempotency/concurrency/authorization/audit results; Farmer/Buyer/Operator validation; migration/backend tests; files changed; branch/commit SHAs; remaining manual QA; working tree; and safety confirmation.
