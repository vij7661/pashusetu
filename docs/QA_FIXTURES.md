# PashuSetu isolated QA fixtures

The manual-QA and automation database is PostgreSQL database `pashusetu_qa`, served by Compose service `db_qa`. It is separate from the existing `db` service and its `pashusetu` database.

Reset, migrate, and seed it from the repository root with:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\reset_qa_db.ps1
```

The command fails closed unless the runtime reports `APP_ENV=qa`, enables both QA isolation and test OTP, and both the configured and actual database names equal `pashusetu_qa`. It never targets the `db` service, drops a database, or uses pilot/production data.

## Canonical synthetic users

| Fixture ID | Role | Local mobile | Language | Intended state |
| --- | --- | --- | --- | --- |
| `FARMER_EN_001` | Farmer | `6123456789` | English | Verified, three-goat lot, live listing |
| `FARMER_TE_001` | Farmer | `7234567890` | Telugu | Role-only user for fresh profile registration |
| `FARMER_SUB3_001` | Farmer | `8345678901` | English | Verified, two-goat/sub-3 draft lot |
| `BUYER_001` | Buyer | `9456789012` | English | Verified synthetic buyer |
| `OPERATOR_001` | Operator | `6789012345` | English | Active at `QA-CENTRE-001` |
| `ADMIN_001` | Admin | `7890123456` | English | Active synthetic admin |

Fresh Farmer UI fields remain empty; testers enter a fixture number deliberately. The QA-only deterministic OTP is `4816`. Seeded fixture numbers can request it, while valid unseeded numbers return `QA_TEST_USER_NOT_FOUND` without creating an OTP challenge. Test OTP mode is rejected in pilot/production configuration.

Stable business fixture codes include `QA-GOAT-EN-001` through `003`, `QA-GOAT-TE-001`, `QA-GOAT-SUB3-001` and `002`, `QA-LOT-EN-003`, `QA-LOT-SUB3-002`, `QA-WEIGHMENT-001`, and `QA-LISTING-LIVE-001`.
