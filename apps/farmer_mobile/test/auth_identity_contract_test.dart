import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_models.dart';

void main() {
  test('parses Farmer auth identity', () {
    final identity = AuthIdentity.fromJson({
      'user_id': 'user-1',
      'mobile_e164': '+919100000001',
      'roles': ['FARMER', 'ADMIN'],
      'preferred_language': 'te',
    });

    expect(identity.userId, 'user-1');
    expect(identity.mobileE164, '+919100000001');
    expect(identity.isFarmer, isTrue);
    expect(identity.roles, ['FARMER', 'ADMIN']);
    expect(identity.preferredLanguage, 'te');
  });

  test('rejects malformed or non-Farmer auth identity', () {
    for (final json in [
      {
        'user_id': 'user-1',
        'mobile_e164': '+919100000001',
        'roles': <String>[],
        'preferred_language': 'te',
      },
      {
        'user_id': 'user-1',
        'mobile_e164': '+919100000001',
        'roles': ['BUYER'],
        'preferred_language': 'te',
      },
      {
        'user_id': 'user-1',
        'mobile_e164': '+919100000001',
        'roles': ['FARMER', 'UNKNOWN'],
        'preferred_language': 'te',
      },
      {
        'user_id': 'user-1',
        'mobile_e164': '9100000001',
        'roles': ['FARMER'],
        'preferred_language': 'te',
      },
      {
        'user_id': 'user-1',
        'mobile_e164': '+919100000001',
        'roles': ['FARMER'],
        'preferred_language': 'xx',
      },
    ]) {
      expect(
        () => AuthIdentity.fromJson(json),
        throwsA(isA<FormatException>()),
      );
    }
  });

  test('rejects empty or whitespace auth tokens', () {
    for (final pair in [
      {'access_token': '', 'refresh_token': 'refresh'},
      {'access_token': 'access', 'refresh_token': ''},
      {'access_token': '   ', 'refresh_token': 'refresh'},
      {'access_token': 'access', 'refresh_token': '   '},
    ]) {
      expect(
        () => TokenPair.fromJson(pair),
        throwsA(isA<FormatException>()),
      );
    }
  });

  test('validates temporary Farmer registration session states', () {
    final details = FarmerRegistrationSession.fromJson({
      'registration_id': 'REG-1',
      'registration_token': 'token',
      'registration_status': 'NEW_IN_PROGRESS',
      'next_step': 'FARMER_DETAILS',
    });
    final kyc = FarmerRegistrationSession.fromJson({
      'registration_id': 'REG-1',
      'registration_token': 'token',
      'registration_status': 'NEW_IN_PROGRESS',
      'next_step': 'KYC',
    });

    expect(details.nextStep, 'FARMER_DETAILS');
    expect(kyc.nextStep, 'KYC');

    expect(
      () => FarmerRegistrationSession.fromJson({
        'registration_id': 'REG-1',
        'registration_token': 'token',
        'registration_status': 'COMPLETED',
        'next_step': 'HOME',
      }),
      throwsA(isA<FormatException>()),
    );
  });
}
