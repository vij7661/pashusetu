class FarmerRegistrationStatus {
  const FarmerRegistrationStatus({
    required this.registrationId,
    required this.registrationStatus,
    required this.nextStep,
    required this.preferredLanguage,
    this.fullName,
    this.village,
    this.mandal,
    this.district,
    this.state,
  });

  final String registrationId;
  final String registrationStatus;
  final String nextStep;
  final String preferredLanguage;
  final String? fullName;
  final String? village;
  final String? mandal;
  final String? district;
  final String? state;

  factory FarmerRegistrationStatus.fromJson(Map<String, dynamic> json) {
    String requiredString(String key) {
      final value = json[key];
      if (value is! String || value.isEmpty) {
        throw FormatException('Invalid farmer registration field: $key');
      }
      return value;
    }

    String? optionalString(String key) {
      final value = json[key];
      if (value == null) return null;
      if (value is! String) {
        throw FormatException('Invalid farmer registration field: $key');
      }
      return value;
    }

    final nextStep = requiredString('next_step');
    if (!const {'FARMER_DETAILS', 'KYC', 'HOME'}.contains(nextStep)) {
      throw FormatException('Invalid farmer registration next_step: $nextStep');
    }

    return FarmerRegistrationStatus(
      registrationId: requiredString('registration_id'),
      registrationStatus: requiredString('registration_status'),
      nextStep: nextStep,
      preferredLanguage: requiredString('preferred_language'),
      fullName: optionalString('full_name'),
      village: optionalString('village'),
      mandal: optionalString('mandal'),
      district: optionalString('district'),
      state: optionalString('state'),
    );
  }
}

class FarmerRegistrationComplete {
  const FarmerRegistrationComplete({
    required this.farmerId,
    required this.kycStatus,
    required this.registrationStatus,
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
  });

  final String farmerId;
  final String kycStatus;
  final String registrationStatus;
  final String accessToken;
  final String refreshToken;
  final String tokenType;

  factory FarmerRegistrationComplete.fromJson(Map<String, dynamic> json) {
    String requiredString(String key) {
      final value = json[key];
      if (value is! String || value.isEmpty) {
        throw FormatException('Invalid farmer registration completion field: $key');
      }
      return value;
    }

    final kycStatus = requiredString('kyc_status');
    if (kycStatus != 'KYC_PENDING') {
      throw FormatException('Unexpected KYC status after submission: $kycStatus');
    }

    final registrationStatus = requiredString('registration_status');
    if (registrationStatus != 'KYC_SUBMITTED') {
      throw FormatException(
        'Unexpected registration status after KYC: $registrationStatus',
      );
    }

    return FarmerRegistrationComplete(
      farmerId: requiredString('farmer_id'),
      kycStatus: kycStatus,
      registrationStatus: registrationStatus,
      accessToken: requiredString('access_token'),
      refreshToken: requiredString('refresh_token'),
      tokenType: requiredString('token_type'),
    );
  }
}
