# PashuSetu — Current Agent Task

**Work item:** GitHub Issue #4 — Local PostgreSQL backend + Farmer integration

**Current objective:** Diagnose and restore the local Docker/backend runtime without changing application source code.

## Instructions

Follow all rules in `/AGENTS.md`.

Do not edit application source code for this task.
Do not commit or push unless this task file is later updated to authorize a code/configuration fix.
Do not delete containers, images, databases, Docker volumes, or data.
Do not change BIOS, WSL, Windows, or Docker Desktop system configuration automatically.

## Execute

1. Inspect and report:
   - `git status`
   - current branch
   - `docker version`
   - `docker context ls`
   - `docker info`
   - `wsl --status`
   - `wsl --version`
   - `wsl -l -v`
   - `docker compose config`
   - `docker compose ps`
2. If Docker is available and Compose validates, use the existing repository configuration to start only the development `db` and `api` services.
3. Wait for/inspect service health.
4. Run existing Alembic migrations through the API container.
5. Call `http://localhost:8000/health`.
6. Run the backend test suite through the existing development/test environment if available.
7. Stop at the first meaningful blocker. Do not improvise destructive/system fixes.

## Completion report

Report:
- Docker/WSL status
- Compose status
- DB status
- API health result
- migration result
- backend test result
- exact blocker if any
- minimal recommended next action
- confirmation that no prohibited actions were performed

Do not claim this work item is complete unless the required checks actually pass.
