# TD-3 — Verified Weighment

## Implemented
- Mandal Centre entity
- Operator profile bound to a centre
- Registered Scale Device entity
- Scale calibration status
- Vendor-neutral `ScaleAdapter`
- Simulated scale adapter for development/tests
- Weighment Session
- Ordered raw weight readings
- Stable-reading validation
- Explicit lock step
- Gross / tare / net weight at fixed precision
- Verification video attachment step
- Farmer review / acknowledgement
- Farmer rejection → reweigh path
- Reweigh links to original session rather than overwriting it
- QR receipt metadata and print status
- PostgreSQL migration + tests
- Operator-role enforcement on session creation, readings, lock, verification-video and reweigh mutations
- Farmer-role enforcement on acknowledgement and receipt issuance
- Farmer ownership verification before acknowledgement or receipt issuance
- Receipt response carries the verified `target_type` and `target_id` so the Farmer app can continue into pricing without re-entering or fabricating the livestock target

## Correct business path

```text
Operator selects Goat/Lot
→ validate centre + scale
→ live readings
→ stable?
    NO → continue live readings
    YES → lock stable reading
→ capture verification video
→ farmer reviews
→ farmer accepts?
    NO → mark rejected and create fresh reweigh
    YES → farmer acknowledgement
→ create receipt carrying verified target identity
→ weighment VERIFIED
→ Farmer app opens Set Price & Listing Rules for that verified target
```

There is **no path from Farmer Acknowledgement back to the scale** after acceptance. The Farmer cannot acknowledge or request a receipt for another Farmer's weighment.

## Authorization boundary

The API now separates the two actors at the trust boundary:

- **Operator mutations:** create session, append readings, lock a reading, attach verification evidence and create reweigh sessions.
- **Farmer mutations:** acknowledge the verified weighment and request its receipt.
- For Farmer mutations, the server resolves the Goat/Lot owner and verifies it matches the authenticated Farmer profile. Client-supplied ownership is never trusted.

Role checks alone are not considered sufficient for Operator-side authorization. A later hardening slice must also enforce that the Operator is permitted to act for the session's assigned centre/operator relationship.

## Evidence
TD-3 reuses `EvidenceAsset` introduced in TD-2. A development evidence asset can be associated with the weighment and marked as `WEIGHMENT_VIDEO`.

## Hardware boundary
The backend defines the scale contract but does not pretend to speak a specific Bluetooth protocol. A real vendor adapter belongs in the Operator app/integration layer once a physical scale model is selected.

## Important production hardening still required
- enforce assigned Operator / centre ownership for each Operator-side session mutation, not only the Operator role
- server-generated audit events for every weighment transition
- idempotency for session creation / lock / acknowledgement / receipt
- signed object-storage video uploads
- actual QR encoding/printing adapter
- scale calibration expiry dates/certificates
- offline queue and sync rules for the Operator app

## Marketplace handoff
A verified Farmer acknowledgement creates a receipt whose target identity is carried directly into the Farmer pricing screen. The listing screen still revalidates the verified weighment context with the backend before publication; navigation context is convenience, not authority.

TD-4 marketplace behavior includes:
- verified listing eligibility
- Admin-curated reference-price metadata during pilot
- Farmer ₹/kg / total price calculation
- server-side listing acknowledgement evidence
- publish/close rules
- search/filter API
- bid command with idempotency key
- server-authoritative sequence
- duplicate retry behavior
- deterministic acceptance with transaction locking
