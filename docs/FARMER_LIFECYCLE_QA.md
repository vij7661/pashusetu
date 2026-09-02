# Farmer Lifecycle QA Addendum

This addendum covers lifecycle/data-dependency QA introduced after the original Farmer manual-QA baseline. It is development/test only.

## Lifecycle checkpoints

| State | Mobile | Dev OTP | Authoritative starting condition | Expected path |
| --- | --- | --- | --- | --- |
| `NEW_NOT_STARTED` | `+919100000001` | `8830` | No registration and no Farmer account | New registration -> Farmer Details |
| `REGISTRATION_STARTED` | `+919100000009` | `0872` | Registration exists; details absent; no Farmer account | Resume -> Farmer Details |
| `DETAILS_COMPLETED` | `+919100000017` | `4856` | Registration + Farmer Details exist; no Farmer account | Resume -> KYC |
| `KYC_PENDING` | `+919100000025` | `1735` | Farmer account exists; KYC pending | Existing Farmer login -> Home with transactional restrictions |
| `KYC_VERIFIED` | `+919100000033` | `0588` | Farmer account exists; KYC verified | Existing Farmer login -> full eligible flow |

Routing is determined by authoritative lifecycle state. OTP verification alone does not make a Farmer an existing account.

## Reset and seed

From repository root:

```bat
copy .env.example .env
docker compose down -v
docker compose up --build -d
docker compose exec api alembic upgrade head
make farmer-qa-seed
```

Without `make`:

```bat
docker compose exec api python scripts/seed_farmer_manual_qa.py
docker compose exec api python scripts/seed_farmer_lifecycle_qa.py
docker compose exec api python scripts/seed_farmer_manual_qa_states.py
docker compose exec api python scripts/seed_farmer_weighment_review_qa.py
docker compose exec api python scripts/verify_farmer_lifecycle_qa.py
```

The headless verifier checks the five lifecycle preconditions without consuming the brand-new identity.

## Manual lifecycle cases

### FLQA-01 - Brand-new Farmer

Use `+919100000001` / `8830` through New Farmer Registration.

Expected: Farmer Details opens. After completing details and KYC, the identity has advanced and must not be reused as `NEW_NOT_STARTED` without a database reset/reseed.

### FLQA-02 - Registration started, details not entered

Use `+919100000009` / `0872` through New Farmer Registration.

Expected: the existing in-progress registration resumes at Farmer Details. It must not restart as a completely new registration and must not be treated as an existing Farmer account.

### FLQA-03 - Details completed, KYC not submitted

Use `+919100000017` / `4856` through New Farmer Registration.

Expected: saved details are preserved and the journey resumes at KYC. No duplicate Farmer account is created.

### FLQA-04 - KYC pending account

Use Existing Farmer Login with `+919100000025` / `1735`.

Expected: Home opens as an existing Farmer; KYC-dependent transaction actions remain blocked according to the authoritative backend contract.

### FLQA-05 - KYC verified account

Use Existing Farmer Login with `+919100000033` / `0588`.

Expected: Home opens as an existing verified Farmer and eligible flows are available subject to their normal domain prerequisites.

## Data-dependency rule

Every QA case must declare its required starting state. Once an action changes authoritative persistent state, later tests must use the resulting state; they must not continue treating the same identity as though it remained in the earlier state. To repeat an earlier lifecycle case, use a fresh controlled identity or explicitly reset/reseed the environment.

Eliminate accidental test dependencies. Legitimate business-flow dependencies must be explicit: prerequisite state -> action -> authoritative transition -> resulting state -> reuse/reset policy.

## Failure handling

If a precondition is not satisfied, do not force the desired path. Record the actual authoritative state and classify the failure as `CODE DEFECT`, `FIXTURE-DATA DEFECT`, `TEST DEFECT`, `ENVIRONMENT-TOOLING DEFECT`, or `REQUIREMENT UNRESOLVED` before correcting the responsible layer.
