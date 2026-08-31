import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/localization/app_strings.dart';
import 'package:pashusetu_farmer/src/core/localization/profile_strings.dart';
import 'package:pashusetu_farmer/src/features/identity/farmer_profile.dart';

void main() {
  test('parses a complete Farmer profile response', () {
    final profile = FarmerProfile.fromJson({
      'farmer_id': 'PS-FRM-TEST',
      'full_name': 'Test Farmer',
      'village': 'Village',
      'mandal': 'Mandal',
      'district': 'District',
      'state': 'Telangana',
      'kyc_status': 'KYC_VERIFIED',
      'payout_status': 'NOT_CONFIGURED',
      'preferred_language': 'te',
    });

    expect(profile.farmerId, 'PS-FRM-TEST');
    expect(profile.fullName, 'Test Farmer');
    expect(profile.kycStatus, 'KYC_VERIFIED');
  });

  test('rejects missing required Farmer identity fields', () {
    expect(
      () => FarmerProfile.fromJson({
        'full_name': 'Test Farmer',
        'kyc_status': 'KYC_VERIFIED',
        'payout_status': 'NOT_CONFIGURED',
        'preferred_language': 'te',
      }),
      throwsFormatException,
    );
  });

  test('profile labels exist for every supported language', () {
    final englishKeys = ProfileStrings.values['en']!.keys.toSet();
    for (final language in AppStrings.supportedLanguages) {
      final strings = ProfileStrings.values[language];
      expect(strings, isNotNull);
      expect(strings!.keys.toSet(), englishKeys);
      for (final key in englishKeys) {
        expect(strings[key]!.trim(), isNotEmpty);
      }
    }
  });
}
