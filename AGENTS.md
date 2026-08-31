# PashuSetu Codex Engineering Contract

This file defines mandatory repository-level rules for every Codex/AI coding task in PashuSetu. These rules apply before, during, and after any implementation or test fix.

## 1. Product contract comes first
- Determine the intended PashuSetu product/domain behavior before changing code or tests.
- Do not treat a failing test as proof that production code is wrong.
- If intended behavior is ambiguous, report the ambiguity instead of inventing a contract.

## 2. Classify failures before fixing
Every failure must be classified, with evidence, as one of:
- CODE_DEFECT
- TEST_EXPECTATION_DEFECT
- FIXTURE_OR_TEST_DATA_DEFECT
- ENVIRONMENT_OR_TOOLING_DEFECT
- PRODUCT_CONTRACT_AMBIGUITY

Do not modify production code until the failure classification supports doing so.

## 3. Architecture boundaries are mandatory
- Keep UI/presentation separate from state, business/domain logic, persistence, APIs, and infrastructure.
- UI/layout/style/label/component changes must not alter authentication, routing, validation, persistence, fixtures, APIs, bidding rules, or other domain contracts.
- Prefer stable interfaces between layers.
- Preserve Android/mobile compatibility for app changes.
- Avoid unrelated refactors while fixing a targeted problem.

## 4. Dynamic and configurable behavior by default
- Prefer configuration, localization resources, domain data, and stable abstractions over scattered hard-coded values.
- Hard-code only genuine stable constants or deliberately controlled development/test constants, and centralize them.
- Never add production hard-coding merely to make a test pass.

Specifically, do not hard-code:
- farmer/buyer identities or profiles
- OTP acceptance/bypasses
- routes/navigation outcomes
- listing/goat/lot values
- prices, bids, weights, or market recommendations
- language/localized content
- IDs or fixture-specific values
- test-only success/failure behavior

## 5. Tests are evidence, not the product specification
- Never weaken, delete, skip, or rewrite a valid test merely to obtain green status.
- A test may be changed only when evidence shows its expectation is inconsistent with the product contract.
- Fixture/test-data changes must remain test-scoped unless the same change is genuinely required by production behavior.
- Do not introduce production branches that detect tests or fixture identities.

## 6. Required implementation sequence
For every task:
1. State the relevant product contract.
2. Inspect the affected implementation and adjacent flow.
3. Reproduce/understand the failure.
4. Classify the root cause.
5. Identify the smallest correct change.
6. Implement without violating architecture boundaries.
7. Run the most targeted relevant tests first.
8. Run the broader regression suite for affected apps/services.
9. Inspect adjacent flows for regression risk.
10. Report evidence and remaining uncertainty.

## 7. Regression discipline
A local green test is not sufficient acceptance evidence.
- Check callers/consumers of changed interfaces.
- Check authentication, routing, validation, persistence, localization, API/domain contracts, and mobile behavior when relevant.
- Do not silently change public/domain contracts.
- When a contract must change, identify all affected consumers and tests explicitly.

## 8. PashuSetu trust-sensitive behavior
Bidding, matching, transaction, verification, and audit behavior are trust-layer functionality.
- Preserve deterministic and replayable matching/bidding behavior.
- Commands/bids should be represented in the authoritative append-only event history as designed, not merely final outcomes.
- Concurrency/priority/acceptance rules must be explicit and deterministic.
- Bid retries must reuse the client-generated idempotency key representing the original user intent.
- Deduplicate at the authoritative sequencer before event-log append.
- Preserve atomic uniqueness/deduplication semantics for bidder + idempotency key.
- Never solve trust-layer failures with UI-only or client-only shortcuts.

## 9. Stop conditions
Stop and report instead of guessing when:
- product behavior is genuinely ambiguous;
- a proposed fix would require weakening a valid contract;
- required fixture/data provenance is unknown;
- a migration or API contract change has unassessed consumers;
- the only apparent solution is a test-specific production bypass;
- the requested change conflicts with these repository rules.

## 10. Required Codex completion report
Every Codex implementation/fix report must include:
- Product contract used
- Root-cause classification
- Evidence for that classification
- Files changed
- Why each production change is necessary
- Tests/fixtures changed and justification, if any
- Targeted tests run and results
- Regression tests run and results
- Adjacent flows checked
- Hard-coded/test-specific behavior introduced: YES/NO (must normally be NO)
- Architecture/mobile compatibility impact
- Remaining risks or uncertainties

A task is not considered complete merely because tests pass. It is complete only when the implementation, tests, fixtures, and product contract agree without violating this engineering contract.
