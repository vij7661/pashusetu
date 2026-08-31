import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_models.dart';

void main() {
  test('parses Farmer auth identity', () {
    final identity = AuthIdentity.fromJson({
      'user_id': 'user-1',
      'mobile_e164': '+919100000001',
      'roles': ['FARMER'],
      'preferred_language': 'te',
    });

    expect(identity.userId, 'user-1');
    expect(identity.mobileE164, '+919100000001');
    expect(identity.isFarmer, isTrue);
    expect(identity.preferredLanguage, 'te');
  });

  test('rejects malformed or non-Farmer auth identity', () {
    expect(
      () => AuthIdentity.fromJson({
        'user_id': 'user-1',
        'mobile_e164': '+919100000001',
        'roles': [],
        'preferred_language': 'te',
      }),
      throwsA(isA<FormatException>()),
    );

    expect(
      () => AuthIdentity.fromJson({
        'user_id': 'user-1',
        'mobile_e164': '+919100000001',
        'roles': ['BUYER'],
        'preferred_language': 'te',
      }),
      throwsA(isA<FormatException>()),
    );

    expect(
      () => AuthIdentity.fromJson({
        'user_id': 'user-1',
        'mobile_e164': '+919100000001',
        'roles': ['FARMER'],
        'preferred_language': 'xx',
      }),
      throwsA(isA<FormatException>()),
    );
  });

  test('rejects empty auth tokens', () {
    expect(
      () => TokenPair.fromJson({
        'access_token': '',
        'refresh_token': 'refresh',
      }),
      throwsA(isA<FormatException>()),
    );
  });
}
