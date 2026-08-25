# API Conventions

- Prefix: `/api/v1`
- JSON REST / OpenAPI
- Public identifiers: UUID/opaque IDs
- Mutation commands, not client-assigned authoritative states
- `X-Request-ID` accepted and returned
- Retry-sensitive endpoints will accept `Idempotency-Key`
- Stable errors:
```json
{
  "code": "LISTING_CLOSED",
  "message": "Listing is closed.",
  "field_errors": {}
}
```
- Money: integer paise in API/domain calculations
- Weight: decimal kg
- Cursor pagination for bids/events/order-sensitive lists
