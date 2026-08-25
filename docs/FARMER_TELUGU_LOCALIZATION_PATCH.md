# Farmer Telugu Localization Patch

This patch makes the selected Farmer language control the UI instead of only storing a language code.

## Fully localized in this patch
- New Farmer onboarding after language selection
- Farmer details
- KYC screen
- payout screen
- registration review
- Home dashboard
- Goat / Lot creation
- Price & Listing Rules
- Farmer acknowledgement
- Dispute
- Settlement

## Current language coverage
English and Telugu are fully populated for the tested Farmer flow.
Other languages remain selectable but fall back to English for keys not yet translated.

## Persistence
The selected language is saved in SharedPreferences and remains selected after navigation/restart.

## Test
```bat
cd apps\farmer_mobile
flutter pub get
flutter analyze
flutter test
flutter run -d chrome
```

Test sequence:
1. New Farmer Registration
2. Choose Telugu
3. Continue to Farmer Details
4. Verify all labels are Telugu
5. Continue through KYC and Payout
6. Open Home and Goat/Lot pages
