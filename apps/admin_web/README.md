# PashuSetu Admin Web — APP-4

React + Vite Admin console connected to the same TD-8 backend.

## Implemented
- Admin login shell
- dashboard
- users / KYC masking view
- Mandal Centres / scale registry view
- authoritative transaction lookup
- bidding audit
- dispute resolution screen
- payment/settlement monitor
- audit event replay
- operator scorecards

## Connected backend endpoints
- `/auth/*`
- `/transaction/*`
- `/bidding/listings/*`
- `/disputes/*`
- `/payments/*`
- `/audit/*`

## Important access-control note
The current backend has role/permission scaffolding, but this APP-4 repository should not be considered production admin security until:
- real admin user provisioning is implemented
- MFA is added
- strict admin-only permission dependencies are enforced on every admin mutation
- audit is emitted for every admin action
- sensitive data access is reviewed

## Run
```bash
npm install
npm run dev
```

Environment:
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Development OTP is `4816`.
