import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/localization/kyc_status_strings.dart';
import 'package:pashusetu_farmer/src/features/identity/farmer_profile.dart';

void main() {
  Map<String, dynamic> validProfile() => {
        'farmer_id': 'FARMER-1',
        'full_name': 'Ramesh Goud',
        'village': 'Chityal',
        'mandal': 'Chityal',
        'district': 'Nalgonda',
        'state': 'Telangana',
        'kyc_status': 'KYC_PENDING',
        'payout_status': 'PENDING',
        'preferred_language': 'te',
      };

  test('parses authoritative Farmer profile lifecycle fields', () {
    final profile = FarmerProfile.fromJson(validProfile());

    expect(profile.kycStatus, 'KYC_PENDING');
    expect(profile.preferredLanguage, 'te');
    expect(KycStatusStrings.statusLabel('te', profile.kycStatus), isNot('KYC_PENDING'));
  });

  test('rejects unknown Farmer KYC state', () {
    final json = validProfile()..['kyc_status'] = 'UNKNOWN_KYC_STATE';
    expect(
      () => FarmerProfile.fromJson(json),
      throwsA(isA<FormatException>()),
    );
  });

  test('rejects unsupported Farmer language', () {
    final json = validProfile()..['preferred_language'] = 'xx';
    expect(
      () => FarmerProfile.fromJson(json),
      throwsA(isA<FormatException>()),
    );
  });
}
