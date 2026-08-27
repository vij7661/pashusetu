# PashuSetu — Agent Operating Rules

This repository is being developed for a controlled goat-procurement marketplace pilot. These rules apply to Codex and any other coding agent working in this repository.

## 1. Source of truth

1. The approved PashuSetu SRS / MVP specification is the requirements authority.
2. GitHub Issues are implementation work orders derived from approved requirements.
3. Do not invent, redesign, or silently change business rules because an implementation seems easier.
4. If a requirement is ambiguous, contradictory, legally sensitive, payment-related, KYC/Aadhaar-related, or affects the transaction trust model, stop and request approval.

## 2. Branching and Git safety

- Never implement directly on `main`.
- Work on the currently approved feature/bugfix branch or create a clearly named branch tied to a GitHub issue.
- Never force-push.
- Never rewrite public history unless explicitly approved.
- Never commit secrets, `.env`, credentials, private keys, tokens, production URLs, or sensitive test data.
- Do not merge PRs unless explicitly instructed.
- Before a commit, inspect the intended diff and ensure unrelated files are excluded. Routine diff inspection does not require human approval.
- Use focused commit messages, for example:
  - `feat(farmer): ...`
  - `fix(buyer): ...`
  - `fix(backend): ...`
  - `test(bidding): ...`
  - `docs: ...`

## 3. Autonomy and approval policy

For an approved task, proceed autonomously through routine, reversible development actions. Do not repeatedly ask the human for permission merely because a command reads files, runs tests, resolves dependencies, starts existing development services, edits in-scope source files, or performs ordinary Git operations on the approved non-main branch.

Allowed without additional approval when needed to complete the current approved task:
- inspect/search/read repository files and Git history/status/diffs
- edit files explicitly within task scope
- create non-destructive temporary/build files required by normal tooling
- `flutter pub get`, analyze, test and normal Flutter build/test commands
- install/resolve project-level dependencies declared by the repository, provided this does not install paid services or change OS/system configuration
- run backend/unit/integration tests
- `docker compose config`, `ps`, logs, and starting/restarting existing development services
- execute existing non-destructive migrations against the local development/test database
- make HTTP calls to local development endpoints
- create/switch approved feature or bugfix branches
- stage, commit and push validated task changes to the approved non-main branch when the current task authorizes implementation/commit
- revert incidental out-of-scope changes caused by tooling

When a tool itself presents a mandatory sandbox/OS security confirmation, request only the minimum permission necessary and continue after approval. Do not ask conversationally for permission again if the user/tool has already authorized that action for the current task.

Use engineering judgment for low-risk implementation details that do not alter approved business behavior. If several equivalent low-risk technical choices exist, choose the smallest/reversible option, test it, and document the choice rather than interrupting the user.

## 4. Change discipline

- Make the smallest change that satisfies the approved task.
- Do not perform opportunistic refactors in unrelated modules.
- Do not change architecture, transaction states, pricing rules, bid policy, dispute rules, KYC behavior, or payment semantics unless the task explicitly authorizes it.
- Generated-file changes must be intentional and explained.
- If tooling changes files outside scope (for example `analysis_options.yaml`), revert those changes unless required.

## 5. Mandatory validation before commit

Run the relevant checks for every changed area.

### Farmer Flutter app
From `apps/farmer_mobile`:

```bash
flutter pub get
flutter analyze
flutter test
```

### Buyer Flutter app
From `apps/buyer_mobile`:

```bash
flutter pub get
flutter analyze
flutter test
```

### Operator Flutter app
From `apps/operator_mobile` when applicable:

```bash
flutter pub get
flutter analyze
flutter test
```

### Backend
Prefer the repository's Docker-backed environment when Docker is available. Typical checks include:

```bash
docker compose config
docker compose ps
docker compose exec api alembic upgrade head
docker compose exec api pytest
```

Run targeted tests first when useful, then the relevant full suite before commit.

If a required runtime is unavailable, do not fake a pass. Report the blocker clearly.

## 6. Docker and database safety

Allowed without special approval when part of an approved task:
- `docker compose config`
- `docker compose ps`
- starting/restarting existing development services
- viewing logs
- running existing non-destructive migrations on development/test databases
- running tests

Require explicit approval before:
- deleting Docker volumes
- `docker system prune`
- dropping databases or schemas
- destructive/reset migrations
- deleting containers/images solely to recover disk space
- modifying Windows/WSL/BIOS/system configuration

Never destroy the local or pilot database as a convenience fix.

## 7. Security and sensitive data

- Never store raw Aadhaar data unless a separately approved compliant design explicitly requires it.
- KYC, payment custody/escrow, OTP providers, storage providers, and other external services must remain behind provider/adaptor boundaries.
- Do not weaken authentication, authorization, idempotency, auditability, or evidence integrity to make a test pass.
- Mask sensitive fields in logs and UI where required.

## 8. Trust-critical rules

Treat the following as high-risk changes requiring careful review and tests:
- bid idempotency
- server-authoritative bid sequencing
- simultaneous bid/offer acceptance
- weighment lock/acknowledgement/reweigh history
- agreement versioning
- transaction-state transitions
- tolerance calculation
- settlement/dispute routing
- append-only audit history

Never use client timestamps to establish commercial priority when the backend is the authority.
Never overwrite an acknowledged/locked weighment to represent a reweigh.
Never silently mutate a locked agreement.

## 9. QA handoff

Development is not complete merely because code compiles.

Before asking for QA:
1. State the branch and commit SHA.
2. List requirement / issue IDs implemented.
3. List changed files or modules.
4. Report automated test results exactly.
5. Report known limitations and untested areas.
6. Provide setup/test instructions needed by QA.

The human QA owner decides acceptance/rejection of the release candidate.

## 10. When to stop and ask for approval

Stop and request explicit human approval only for materially risky or irreversible actions, including:
- destructive commands or data deletion
- production/pilot deployment or public release
- merging to `main`
- force-push/history rewrite
- changing approved business rules or resolving material requirement ambiguity by assumption
- schema-destructive migrations
- real payment/KYC/Aadhaar integrations or handling real sensitive credentials/data
- introducing paid infrastructure/services or actions likely to incur charges
- changing secrets, cloud-account configuration, Windows/WSL/BIOS/security configuration
- disabling security controls or materially weakening authentication/authorization/auditability

Do not stop for routine development permissions that are already covered by the approved task and the autonomy policy above.

## 11. Pilot-week priority

For the controlled pilot build, prioritize the golden path and pilot blockers over polish:

Farmer registration → goat/lot → Operator verification/weighment → Farmer acknowledgement → listing → multiple Buyer bids → exactly one accepted offer → agreement → pickup/delivery evidence → tolerance → settlement/dispute → Admin audit trail.

Do not add new product features during the pilot-week implementation unless explicitly approved.
