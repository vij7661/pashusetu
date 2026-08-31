import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_models.dart';

void main() {
  test('parses a valid Farmer registration session', () {
    final session = FarmerRegistrationSession.fromJson({
      'registration_id': 'REG-001',
      'registration_token': 'token-123',
      'registration_status': 'NEW_IN_PROGRESS',
      'next_step': 'KYC',
    });

    expect(session.registrationId, 'REG-001');
    expect(session.registrationToken, 'token-123');
    expect(session.registrationStatus, 'NEW_IN_PROGRESS');
    expect(session.nextStep, 'KYC');
  });

  test('rejects an unknown registration next step', () {
    expect(
      () => FarmerRegistrationSession.fromJson({
        'registration_id': 'REG-001',
        'registration_token': 'token-123',
        'registration_status': 'NEW_IN_PROGRESS',
        'next_step': 'UNKNOWN',
      }),
      throwsFormatException,
    );
  });

  test('rejects an empty registration token', () {
    expect(
      () => FarmerRegistrationSession.fromJson({
        'registration_id': 'REG-001',
        'registration_token': '',
        'registration_status': 'NEW_IN_PROGRESS',
        'next_step': 'FARMER_DETAILS',
      }),
      throwsFormatException,
    );
  });
}
