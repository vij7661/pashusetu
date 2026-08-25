# APP-4 Admin Integration

The Admin Web Console completes the four-client MVP surface:
- Farmer
- Buyer
- Operator
- Admin

## Admin responsibilities
Admin is an exception/control surface, not the normal transaction engine.

It can inspect:
- users and KYC status
- centres and scales
- authoritative transaction state
- bid sequence history
- disputes and evidence
- settlement output
- audit events
- operator quality indicators

## Trust rule
Normal state progression belongs to backend domain rules.
Admin overrides, where allowed, must be explicit, permissioned and audited.
