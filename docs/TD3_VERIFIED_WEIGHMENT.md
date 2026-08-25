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
→ create receipt
→ weighment VERIFIED
```

There is **no path from Farmer Acknowledgement back to the scale**.

## Evidence
TD-3 reuses `EvidenceAsset` introduced in TD-2. A development evidence asset can be associated with the weighment and marked as `WEIGHMENT_VIDEO`.

## Hardware boundary
The backend defines the scale contract but does not pretend to speak a specific Bluetooth protocol. A real vendor adapter belongs in the Operator app/integration layer once a physical scale model is selected.

## Important production hardening still required
- authorization checks ensuring only the assigned operator/centre may mutate a session
- server-generated audit events for every transition
- idempotency for session creation / lock / acknowledgement / receipt
- signed object-storage video uploads
- actual QR encoding/printing adapter
- scale calibration expiry dates/certificates
- offline queue and sync rules for the Operator app

## Next slice: TD-4 Marketplace & Bidding
- verified listing eligibility
- market-price recommendation metadata
- farmer ₹/kg / total price calculation
- publish/close rules
- search/filter API
- bid command with idempotency key
- server-authoritative sequence
- duplicate retry behavior
- deterministic acceptance with transaction locking
