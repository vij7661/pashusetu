import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/identity/farmer_registration.dart';

void main() {
  test('accepts in-progress registration before details', () {
    final status = FarmerRegistrationStatus.fromJson({
      'registration_id': 'REG-1',
      'registration_status': 'NEW_IN_PROGRESS',
      'next_step': 'FARMER_DETAILS',
      'preferred_language': 'te',
      'full_name': null,
      'village': null,
      'mandal': null,
      'district': null,
      'state': 'Telangana',
    });

    expect(status.nextStep, 'FARMER_DETAILS');
  });

  test('accepts saved details only when next step is KYC', () {
    final status = FarmerRegistrationStatus.fromJson({
      'registration_id': 'REG-1',
      'registration_status': 'NEW_IN_PROGRESS',
      'next_step': 'KYC',
      'preferred_language': 'en',
      'full_name': 'Ramesh Goud',
      'village': 'Chityal',
      'mandal': 'Chityal',
      'district': 'Nalgonda',
      'state': 'Telangana',
    });

    expect(status.nextStep, 'KYC');
  });

  test('rejects inconsistent lifecycle and unsupported language', () {
    expect(
      () => FarmerRegistrationStatus.fromJson({
        'registration_id': 'REG-1',
        'registration_status': 'NEW_IN_PROGRESS',
        'next_step': 'HOME',
        'preferred_language': 'te',
        'full_name': null,
      }),
      throwsA(isA<FormatException>()),
    );

    expect(
      () => FarmerRegistrationStatus.fromJson({
        'registration_id': 'REG-1',
        'registration_status': 'NEW_IN_PROGRESS',
        'next_step': 'FARMER_DETAILS',
        'preferred_language': 'xx',
        'full_name': null,
      }),
      throwsA(isA<FormatException>()),
    );
  });

  test('KYC completion requires bearer token type', () {
    expect(
      () => FarmerRegistrationComplete.fromJson({
        'farmer_id': 'PS-F-1',
        'kyc_status': 'KYC_PENDING',
        'registration_status': 'KYC_SUBMITTED',
        'access_token': 'access',
        'refresh_token': 'refresh',
        'token_type': 'basic',
      }),
      throwsA(isA<FormatException>()),
    );
  });
}
