# Farmer Flutter 3.47 Compatibility Patch

Applied fixes:
- intl ^0.20.3
- async BuildContext mounted guard
- DropdownButtonFormField value -> initialValue in 4 screens
- const dashboard Row

Run:
```bat
cd apps\farmer_mobile
flutter pub get
flutter analyze
flutter test
flutter run -d chrome
```
