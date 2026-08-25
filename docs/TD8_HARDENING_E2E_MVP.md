# TD-8 — Hardening & End-to-End MVP

## Implemented in this milestone
- reusable RBAC permission map
- inactive-user blocking
- generic durable idempotency helper
- object-storage abstraction
- development upload adapter
- notification-provider abstraction
- development notification adapter
- shared domain-event helpers
- transaction close endpoint
- Farmer/Buyer reputation update on close
- demo seed data
- PostgreSQL integration-test scaffolding
- happy-path and dispute-path state-contract tests
- permission tests
- storage/notification tests
- OpenAPI export script
- GitHub Actions backend CI
- separate PostgreSQL test service

## End-to-end MVP contract

### Happy path
```text
Farmer / Buyer identities
→ individual goat or lot
→ Mandal Centre verified weighment
→ farmer acknowledgement
→ verified listing
→ buyer bid
→ server sequence
→ deterministic acceptance
→ transaction
→ dual-confirmed agreement
→ secured funds
→ transporter assignment
→ pickup evidence
→ in transit
→ delivery verification
→ delivery weighment
→ tolerance within limit
→ settlement
→ closed transaction
→ reputation update
```

### Dispute path
```text
delivery weighment
→ outside tolerance
→ DISPUTED
→ evidence
→ controlled reweigh
→ independent reweigh if needed
→ resolution
→ adjustment
→ settlement
→ close
```

## What "MVP codebase" means here
The repository now has the domain skeleton for the full approved transaction.

It is **not yet production-ready** because real-world providers/hardware remain unselected:
- SMS / WhatsApp
- KYC / Aadhaar verification
- payment/secured-funds provider
- cloud object storage
- Bluetooth scale vendor protocol
- QR printer integration
- maps/geocoding
- push notifications

The architecture keeps these behind adapters so the core domain does not depend on one vendor.

## Required before pilot
1. Choose physical scale and implement Operator-side adapter.
2. Choose cloud/environment.
3. Choose OTP/messaging provider.
4. Finalize compliant KYC approach.
5. Finalize payment/settlement approach.
6. Replace dev storage adapter with signed object-storage uploads.
7. Run migrations and PostgreSQL integration suite in CI.
8. Implement full audit emission on every critical command.
9. Run bid concurrency/load tests.
10. Security review and threat-model closure.
11. Field-test with real operators/farmers/buyers.
12. Validate legal/compliance requirements.

## Recommended next engineering phase
**APP-1: Connect the approved Farmer UI to the real APIs.**

Then:
- APP-2 Buyer
- APP-3 Operator
- APP-4 Admin
- PILOT-1 physical scale + provider integration
