# PashuSetu Farmer App — APP-1.1

The Farmer app is connected to the approved MVP backend journey: registration/KYC lifecycle, livestock, verified weighment acknowledgement, listing, offers, agreement, transaction tracking, dispute and settlement.

## Implemented
- resumable new-Farmer registration and existing-Farmer login
- KYC-pending Home with server-side transaction blocking
- individual Goat and Lot creation
- Operator-created weighment acknowledgement and receipt flow
- camera/evidence upload contract
- authoritative verified-weight listing creation and Farmer acknowledgement gating
- Farmer-owned listing history and Buyer Offers
- accepted offer → authoritative transaction
- Farmer transaction history
- agreement creation / Farmer confirmation
- shipment / transaction-state tracking
- dispute and settlement screens
- six-language string scaffold: Telugu, Hindi, English, Marathi, Tamil, Malayalam

## Manual QA

Use the controlled setup, accounts, OTPs and test cases in:

`docs/FARMER_MANUAL_QA.md`

Android emulator:

```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

Development OTPs are account-specific and deterministic only in explicit local/test environments; there is no universal Farmer OTP.

## Important boundaries

This manual-QA build does not pretend to provide real Aadhaar/KYC verification, real bank/UPI payout onboarding, live push/SMS/WhatsApp delivery, live transporter GPS or real Bluetooth scale integration. Those remain behind provider/hardware boundaries and are required before pilot/production readiness.
