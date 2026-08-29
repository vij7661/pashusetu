# PashuSetu — ChatGPT / Codex / GitHub Operating Workflow

## Purpose

Reduce manual copy-paste between product/design discussion and local coding execution while preserving human QA and explicit approval for risky actions.

## Roles

### ChatGPT
- requirements analysis
- SRS and design authority support
- GitHub issue/branch/PR coordination
- code and architecture review
- CI review
- defect analysis
- acceptance-criteria definition

### Codex CLI
- local repository inspection
- source-code edits
- Git operations on approved branches
- Flutter commands
- Docker/Compose commands
- backend migrations/tests
- local diagnostics
- creation of focused commits and branch pushes when authorized

### Human QA / Product owner
- requirement approval
- QA execution
- exploratory/negative/regression testing
- defect severity/priority
- retest and acceptance
- explicit approval for destructive, production, financial, identity/KYC, or infrastructure actions

## Synchronization mechanism

GitHub is the shared synchronization layer.

1. Requirement or defect is defined and linked to a GitHub Issue.
2. Work happens on a non-main branch.
3. Codex reads `AGENTS.md` automatically as repository guidance.
4. Codex implements and validates locally.
5. Codex commits and pushes the approved branch when instructed.
6. ChatGPT reviews the GitHub diff/PR and CI results.
7. Human QA receives a release candidate and test scope.
8. QA defects become bugfix work; accepted work proceeds toward merge/release.

## Standard task lifecycle

### A. Before coding
- Confirm task/issue and acceptance criteria.
- Confirm current branch is not `main`.
- Confirm working tree state.
- Read `AGENTS.md`.
- Identify affected modules and test commands.

### B. During coding
- Keep scope narrow.
- Do not resolve product ambiguity by assumption.
- Run targeted tests as changes are made.
- Preserve backend authority, idempotency, immutability and audit rules.

### C. Before commit
Codex should report:
- `git status`
- concise diff summary
- files changed
- analyzer/linter results
- unit/integration test results
- any skipped validation and why

### D. Commit / push
Only after the requested validation passes:
- create a focused commit
- push the current non-main branch
- report branch + commit SHA
- do not merge automatically

### E. Review
ChatGPT reviews:
- requirement alignment
- diff scope
- architecture/business-rule impact
- CI results
- security/trust implications

### F. QA handoff
Provide:
- build/release-candidate identifier
- branch and commit SHA
- requirement/issue IDs
- environment/startup instructions
- test data assumptions
- known limitations

## Approval boundaries

Codex must request human approval before:
- merging to `main`
- destructive Docker/database commands
- schema-destructive migrations
- Windows/WSL/BIOS configuration changes
- cloud infrastructure creation/deletion that may incur charges
- production deployment
- adding or changing real payment/KYC/Aadhaar providers
- accessing or modifying secrets
- changing approved business rules

## Pilot-week execution order

1. Stabilize local development/runtime environment.
2. Farmer registration and livestock creation.
3. Operator verification and simulated trusted weighment.
4. Farmer acknowledgement/reweigh.
5. Listing and Buyer discovery.
6. Multiple Buyer bids, idempotency and single acceptance.
7. Agreement and transaction states.
8. Simulated funds, pickup and delivery.
9. Tolerance, settlement/dispute path.
10. Admin audit visibility.
11. Regression/bugfix only before pilot release candidate.

No nonessential feature expansion during the pilot week.
