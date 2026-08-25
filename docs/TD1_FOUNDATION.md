# TD-1 Foundation Decisions

This scaffold follows the approved Technical Design v1.0:

1. **Modular monolith** for MVP.
2. **FastAPI + PostgreSQL** as the core backend stack.
3. **One authoritative backend transaction state** shared by Farmer, Buyer, Operator and Admin.
4. **Append-only audit history** alongside normalized current-state tables.
5. **Retry-sensitive writes** will use durable PostgreSQL idempotency/uniqueness, not Redis alone.
6. **Bid sequencing** will be server authoritative.
7. **KYC/Aadhaar** remains behind a provider/compliance boundary; raw Aadhaar storage is not part of this foundation.
8. **Payments** remain behind an adapter; no claim of escrow until a provider/legal model supports it.
9. **Scale hardware** will use a vendor-neutral `ScaleAdapter` abstraction in the Operator milestone.
10. **Money** will be represented in integer paise and **weight** in fixed-precision decimal in domain modules.

## Next implementation slice (TD-2)
Recommended:
- Farmer/Buyer profile domain
- Individual goat + lot schema
- Core evidence metadata
- Weighment schema
- Listing schema
- Initial domain migration
- API contracts for create goat/lot and verification request
