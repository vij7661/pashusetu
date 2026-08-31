import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/identity/farmer_registration.dart';

void main() {
  test('registration status parses authoritative lifecycle state', () {
    final status = FarmerRegistrationStatus.fromJson({
      'registration_id': 'REG-1',
      'registration_status': 'NEW_IN_PROGRESS',
      'next_step': 'KYC',
      'full_name': 'Ramesh Goud',
      'village': 'Chityal',
      'mandal': 'Chityal',
      'district': 'Nalgonda',
      'state': 'Telangana',
      'preferred_language': 'te',
    });

    expect(status.nextStep, 'KYC');
    expect(status.fullName, 'Ramesh Goud');
    expect(status.preferredLanguage, 'te');
  });

  test('registration status rejects unknown next step', () {
    expect(
      () => FarmerRegistrationStatus.fromJson({
        'registration_id': 'REG-1',
        'registration_status': 'NEW_IN_PROGRESS',
        'next_step': 'LISTING',
        'preferred_language': 'te',
      }),
      throwsFormatException,
    );
  });

  test('KYC completion requires pending identity lifecycle result', () {
    final result = FarmerRegistrationComplete.fromJson({
      'farmer_id': 'PS-F-TEST',
      'kyc_status': 'KYC_PENDING',
      'registration_status': 'KYC_SUBMITTED',
      'access_token': 'access',
      'refresh_token': 'refresh',
      'token_type': 'bearer',
    });

    expect(result.kycStatus, 'KYC_PENDING');
    expect(result.registrationStatus, 'KYC_SUBMITTED');
  });

  test('KYC completion rejects contradictory server state', () {
    expect(
      () => FarmerRegistrationComplete.fromJson({
        'farmer_id': 'PS-F-TEST',
        'kyc_status': 'KYC_VERIFIED',
        'registration_status': 'KYC_SUBMITTED',
        'access_token': 'access',
        'refresh_token': 'refresh',
        'token_type': 'bearer',
      }),
      throwsFormatException,
    );
  });
}
