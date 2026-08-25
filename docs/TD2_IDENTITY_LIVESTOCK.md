# TD-2 — Identity & Livestock

## Implemented
- Farmer profile domain
- Buyer/business profile domain
- Approved six language codes
- Individual Goat entity
- Multi-goat Lot entity
- Optional Goat → Lot membership
- Evidence metadata entity
- Development upload-contract endpoint
- PostgreSQL migration
- Real API contracts for profile, goat, lot and evidence creation

## Farmer onboarding behavior
Existing users do not repeat profile/KYC/payout onboarding during normal login.
New farmers can create a profile after authentication.

## KYC boundary
`kyc_status` is stored as a status only. Raw Aadhaar storage is intentionally absent.
A later provider adapter owns the actual compliant verification workflow.

## Evidence upload
The API now creates evidence metadata and a storage key.
The returned local upload URL is a **development placeholder**.
TD-3/infra work should replace this with object-storage presigned PUT URLs.

## Individual goats and lots
- Individual: `Goat`
- Multi-goat: `Lot`
- `LotGoat` links individually identified goats to a lot where needed.
- Lots can also represent declared quantity before every animal has an individual Goat ID.

## Next slice: TD-3 Weighment
- Mandal Centre + Operator entities
- Scale registry + calibration status
- Weighment session
- stable-reading lock
- gross/tare/net fixed precision
- server timestamp
- verification evidence
- farmer acknowledgement
- immutable reweigh events
- QR receipt reference
