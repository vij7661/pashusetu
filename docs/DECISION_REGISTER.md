# Setugo Decision Register

This file is the authoritative record for high-impact product, architecture, trust, security and business decisions. Legacy repository/package identifiers may still use `pashusetu`; they do not define the current product name.

Status flow: `PROPOSED -> DEBATED -> LOCKED -> SUPERSEDED`.

## DR-001 — Product name
- Date: 2026-08-29
- Status: LOCKED
- Current decision: Public/product name is **Setugo**.
- Supersedes: PashuSetu as a public/product name.
- Notes: `PashuSetu` may remain only in legacy repository, package, branch or historical artifact identifiers until deliberately migrated.

## DR-002 — Pilot reference price authority
- Status: LOCKED
- Decision: Farmer pricing guidance uses an **Admin-curated Reference Price** with source/evidence and effective date. It must not be represented as an online-derived or statistically computed market average until Setugo has sufficient verified transaction data and a defined calculation contract.

## DR-003 — Farmer identity and KYC lifecycle
- Status: LOCKED
- Decision: Permanent Farmer identity is created at/after KYC submission. Before KYC submission only temporary registration state exists. `KYC_PENDING` may enter Home/livestock flows but cannot perform transaction-producing actions until `KYC_VERIFIED`.

## DR-004 — Agreement commercial-term authority
- Status: LOCKED
- Decision: Platform/commercial agreement terms are backend-owned. Mobile supplies only transaction-specific inputs and cannot override platform terms.

## DR-005 — Farmer settlement UI authority
- Status: LOCKED
- Decision: Farmer settlement UI is read-only. A read-looking Farmer screen must not trigger settlement creation or mutation.

## DR-006 — Shipment evidence authority
- Status: LOCKED
- Decision: Shipment milestones must be shown only from backend-evidenced events. Farmer UI must not infer pickup, transit, delivery, weighment or evidence milestones from static UI steps.

## DR-007 — Transaction close authority
- Date: 2026-08-31
- Status: LOCKED
- Decision: Final transaction closure is a **backend/system-owned transition after settlement finality**. Farmer or Buyer must not unilaterally call a public close mutation. Reputation processing is triggered by the authoritative backend close step.
- Supersedes: Party-callable `POST /transaction/{transaction_id}/close` behavior.
- Reasoning: Closure is financially and reputationally final. Allowing either party to close unilaterally makes reputation effects depend on client action rather than backend-confirmed settlement finality.
- Implementation contract:
  - no party-facing close endpoint,
  - no Farmer mobile close method,
  - settlement workflow transitions eligible `SETTLED` transactions to `CLOSED`,
  - reputation processing runs from the backend finalization path.

## DR-008 — Dispute resolution authority
- Date: 2026-08-31
- Status: LOCKED
- Decision: Farmer and Buyer may open disputes and submit transaction evidence, but **final dispute resolution and settlement adjustment are platform-controlled**. A transaction party must not set the final decision, resolution rule or settlement adjustment.
- Supersedes: Party-callable dispute resolution behavior.
- Reasoning: A disputing party cannot be authoritative over its own financial adjustment. Resolution affects money, finality and reputation and therefore requires a trusted platform boundary.
- Implementation contract:
  - dispute opening remains available to verified transaction parties,
  - evidence/reweigh attachment remains ownership-checked,
  - `POST /disputes/{dispute_id}/resolve` requires an authorized platform role,
  - pilot platform resolvers are `ADMIN` or `OPERATOR`,
  - final decision and settlement adjustment remain backend-audited inputs from the resolver workflow.

## Unresolved decisions

### U-001 — Payout/UPI persistence mechanism
Status: UNRESOLVED. Select provider tokenization, encrypted VPA or another compliant mechanism before production payout setup.

### U-002 — Settlement trigger authority/provider mechanism
Status: UNRESOLVED. The Farmer UI is read-only, but the final actor/provider contract that creates/settles payment records still requires an explicit product/security/provider decision.

### U-003 — Aadhaar/KYC legal/provider mechanism
Status: UNRESOLVED. Raw Aadhaar is not persisted in the core backend. Exact compliant provider/legal workflow remains to be selected.

### U-004 — Listing window
Status: UNRESOLVED. Current code contains an 8-hour window, but this is not treated as a locked business rule until explicitly decided.

### U-005 — Exact transaction commission
Status: UNRESOLVED. Planning range remains 1–1.5%; no single exact percentage is locked.
