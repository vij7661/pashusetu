class TokenPair {
  TokenPair({required this.accessToken, required this.refreshToken});

  final String accessToken;
  final String refreshToken;

  factory TokenPair.fromJson(Map<String, dynamic> json) {
    final accessToken = json['access_token'];
    final refreshToken = json['refresh_token'];
    if (accessToken is! String || accessToken.isEmpty) {
      throw const FormatException('Invalid access token');
    }
    if (refreshToken is! String || refreshToken.isEmpty) {
      throw const FormatException('Invalid refresh token');
    }
    return TokenPair(
      accessToken: accessToken,
      refreshToken: refreshToken,
    );
  }
}

class AuthIdentity {
  const AuthIdentity({
    required this.userId,
    required this.mobileE164,
    required this.roles,
    required this.preferredLanguage,
  });

  final String userId;
  final String mobileE164;
  final List<String> roles;
  final String preferredLanguage;

  bool get isFarmer => roles.contains('FARMER');

  factory AuthIdentity.fromJson(Map<String, dynamic> json) {
    String requiredString(String key) {
      final value = json[key];
      if (value is! String || value.isEmpty) {
        throw FormatException('Invalid auth identity field: $key');
      }
      return value;
    }

    final rawRoles = json['roles'];
    if (rawRoles is! List ||
        rawRoles.isEmpty ||
        rawRoles.any((role) => role is! String || role.isEmpty)) {
      throw const FormatException('Invalid auth identity roles');
    }
    final roles = rawRoles.cast<String>();
    const allowedRoles = {'FARMER', 'BUYER', 'OPERATOR', 'ADMIN'};
    if (roles.any((role) => !allowedRoles.contains(role))) {
      throw const FormatException('Unsupported auth identity role');
    }
    if (!roles.contains('FARMER')) {
      throw const FormatException('Farmer role is required for Farmer app identity');
    }

    final preferredLanguage = requiredString('preferred_language');
    if (!const {'te', 'hi', 'en', 'mr', 'ta', 'ml'}.contains(preferredLanguage)) {
      throw FormatException('Unsupported auth identity language: $preferredLanguage');
    }

    return AuthIdentity(
      userId: requiredString('user_id'),
      mobileE164: requiredString('mobile_e164'),
      roles: roles,
      preferredLanguage: preferredLanguage,
    );
  }
}

class FarmerRegistrationSession {
  const FarmerRegistrationSession({
    required this.registrationId,
    required this.registrationToken,
    required this.registrationStatus,
    required this.nextStep,
  });

  final String registrationId;
  final String registrationToken;
  final String registrationStatus;
  final String nextStep;

  factory FarmerRegistrationSession.fromJson(Map<String, dynamic> json) {
    String requiredString(String key) {
      final value = json[key];
      if (value is! String || value.isEmpty) {
        throw FormatException('Invalid farmer registration session field: $key');
      }
      return value;
    }

    final registrationStatus = requiredString('registration_status');
    if (registrationStatus != 'NEW_IN_PROGRESS') {
      throw FormatException(
        'Invalid farmer registration status: $registrationStatus',
      );
    }

    final nextStep = requiredString('next_step');
    if (!const {'FARMER_DETAILS', 'KYC'}.contains(nextStep)) {
      throw FormatException('Invalid farmer registration next_step: $nextStep');
    }

    return FarmerRegistrationSession(
      registrationId: requiredString('registration_id'),
      registrationToken: requiredString('registration_token'),
      registrationStatus: registrationStatus,
      nextStep: nextStep,
    );
  }
}
