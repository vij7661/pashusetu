# PashuSetu — Agent Operating Rules

This repository is being developed for a controlled goat-procurement marketplace pilot. These rules apply to Codex and any other coding agent working in this repository.

## 1. Source of truth

1. The approved PashuSetu SRS / MVP specification is the requirements authority.
2. GitHub Issues are implementation work orders derived from approved requirements.
3. `docs/NEXT_TASK.md` is the current executable work order for the local agent.
4. `docs/AGENT_REPORT.md` is the execution mailbox used to report results back through GitHub.
5. Do not invent, redesign, or silently change business rules because an implementation seems easier.
6. If a requirement is ambiguous, contradictory, legally sensitive, payment-related, KYC/Aadhaar-related, or affects the transaction trust model, stop and request approval.

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

## 4. Task start and automatic handoff

### Task start (mandatory)
Whenever the human gives the single trigger `Read AGENTS.md and execute docs/NEXT_TASK.md. Follow automatic task handoff after PASS.` or an equivalent instruction:

1. First inspect `git status`.
2. If the working tree contains unexpected/uncommitted user changes that make a safe fast-forward pull impossible, stop and report them rather than discarding or overwriting them.
3. Otherwise run `git pull --ff-only` on the current approved branch before reading/executing the task.
4. Re-read the freshly synchronized `AGENTS.md` and `docs/NEXT_TASK.md` after the pull.
5. Execute the current `READY` task.

The human should not need to run a separate `git pull` command before triggering a task.

### Automatic handoff after PASS
After a task reaches `PASS`:

1. Update `docs/AGENT_REPORT.md` with the completed Task ID, validation results, changed files, commit SHA and safety confirmation.
2. Commit and push the validated task changes/report when the task authorizes a push.
3. Run `git pull --ff-only` on the same approved branch.
4. Re-read `AGENTS.md` and `docs/NEXT_TASK.md`.
5. If `NEXT_TASK.md` has `Status: READY` and its `Task ID` differs from the Task ID just completed, immediately execute that new task under these rules without asking the human to trigger it again.
6. Repeat the report → push → pull → check cycle after each successful task.
7. If the Task ID is unchanged, the status is not `READY`, or no new task has been published, stop cleanly and wait.
8. On `BLOCKED` or `FAILED`, publish `AGENT_REPORT.md` and stop. Do not skip ahead to later work because doing so could hide a dependency failure.
9. Do not poll GitHub indefinitely. Perform the post-success pull/check once per completed task. A later task needs a new local trigger unless it was already published before that check.

This creates an automatic chain whenever ChatGPT/GitHub has already published the next work order, without creating an uncontrolled background loop.

## 5. Change discipline

- Make the smallest change that satisfies the approved task.
- Do not perform opportunistic refactors in unrelated modules.
- Do not change architecture, transaction states, pricing rules, bid policy, dispute rules, KYC behavior, or payment semantics unless the task explicitly authorizes it.
- Generated-file changes must be intentional and explained.
- If tooling changes files outside scope (for example `analysis_options.yaml`), revert those changes unless required.

## 6. Mandatory validation before commit

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

## 7. Docker and database safety

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

## 8. Security and sensitive data

- Never store raw Aadhaar data unless a separately approved compliant design explicitly requires it.
- KYC, payment custody/escrow, OTP providers, storage providers, and other external services must remain behind provider/adaptor boundaries.
- Do not weaken authentication, authorization, idempotency, auditability, or evidence integrity to make a test pass.
- Mask sensitive fields in logs and UI where required.

## 9. Trust-critical rules

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

## 10. Agent execution report (mandatory)

At the end of every task execution, update `docs/AGENT_REPORT.md` with a concise machine-readable/human-readable report. This file is the handoff channel to ChatGPT/GitHub review and must be committed and pushed on the current approved non-main branch whenever repository push access is available.

The report MUST contain:
- Task ID / work item and current objective
- timestamp
- branch name
- status: `PASS`, `BLOCKED`, or `FAILED`
- commands/checks executed (summarized; do not paste secrets)
- environment/service status relevant to the task
- files changed
- exact automated test/analyze/lint results
- blocker/error, if any
- recommended next action
- commit SHA if code/report changes were committed
- whether the working tree is clean
- explicit confirmation that no prohibited/destructive actions were performed

If the task is blocked before any source change, still update and push `docs/AGENT_REPORT.md` unless doing so is itself impossible. Do not make unrelated code changes just to publish the report.

Do not put secrets, tokens, private keys, raw Aadhaar, credentials, or sensitive personal data in the report.

## 11. QA handoff

Development is not complete merely because code compiles.

Before asking for QA:
1. State the branch and commit SHA.
2. List requirement / issue IDs implemented.
3. List changed files or modules.
4. Report automated test results exactly.
5. Report known limitations and untested areas.
6. Provide setup/test instructions needed by QA.

The human QA owner decides acceptance/rejection of the release candidate.

## 12. When to stop and ask for approval

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

## 13. Pilot-week priority

For the controlled pilot build, prioritize the golden path and pilot blockers over polish:

Farmer registration → goat/lot → Operator verification/weighment → Farmer acknowledgement → listing → multiple Buyer bids → exactly one accepted offer → agreement → pickup/delivery evidence → tolerance → settlement/dispute → Admin audit trail.

Do not add new product features during the pilot-week implementation unless explicitly approved.
