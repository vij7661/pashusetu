class TokenPair {
  TokenPair({required this.accessToken, required this.refreshToken});

  final String accessToken;
  final String refreshToken;

  factory TokenPair.fromJson(Map<String, dynamic> json) => TokenPair(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
      );
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

    final nextStep = requiredString('next_step');
    if (!const {'FARMER_DETAILS', 'KYC', 'HOME'}.contains(nextStep)) {
      throw FormatException('Invalid farmer registration next_step: $nextStep');
    }

    return FarmerRegistrationSession(
      registrationId: requiredString('registration_id'),
      registrationToken: requiredString('registration_token'),
      registrationStatus: requiredString('registration_status'),
      nextStep: nextStep,
    );
  }
}
