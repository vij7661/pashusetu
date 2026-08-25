# APP-1.1 Farmer Completion

## Farmer flow now represented in Flutter

Welcome
→ New / Existing Farmer
→ Home
→ Add Individual Goat or Lot
→ Upload livestock evidence
→ Operator performs verified weighment
→ Farmer opens acknowledgement screen
→ I acknowledge
→ receipt
→ price/listing
→ market recommendation or own ₹/kg
→ total value
→ publish
→ offers
→ accept
→ transaction
→ agreement
→ shipment tracking
→ settlement OR dispute

## Architectural rule
The app renders server-owned commercial state. It does not locally decide:
- verified weight
- bid order
- winning bid
- agreement lock
- transaction state
- tolerance result
- settlement amount
