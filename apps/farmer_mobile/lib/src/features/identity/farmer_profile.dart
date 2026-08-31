class FarmerProfile {
  const FarmerProfile({
    required this.farmerId,
    required this.fullName,
    required this.village,
    required this.mandal,
    required this.district,
    required this.state,
    required this.kycStatus,
    required this.payoutStatus,
    required this.preferredLanguage,
  });

  final String farmerId;
  final String fullName;
  final String? village;
  final String? mandal;
  final String? district;
  final String? state;
  final String kycStatus;
  final String payoutStatus;
  final String preferredLanguage;

  factory FarmerProfile.fromJson(Map<String, dynamic> json) {
    String requiredString(String key) {
      final value = json[key];
      if (value is! String || value.trim().isEmpty) {
        throw FormatException('Missing or invalid $key');
      }
      return value.trim();
    }

    String? optionalString(String key) {
      final value = json[key];
      if (value == null) return null;
      if (value is! String) throw FormatException('Invalid $key');
      final trimmed = value.trim();
      return trimmed.isEmpty ? null : trimmed;
    }

    final kycStatus = requiredString('kyc_status');
    if (!const {
      'KYC_PENDING',
      'KYC_VERIFIED',
      'KYC_ACTION_REQUIRED',
      'KYC_REJECTED',
    }.contains(kycStatus)) {
      throw FormatException('Invalid Farmer KYC status: $kycStatus');
    }

    final preferredLanguage = requiredString('preferred_language');
    if (!const {'te', 'hi', 'en', 'mr', 'ta', 'ml'}.contains(preferredLanguage)) {
      throw FormatException('Unsupported Farmer language: $preferredLanguage');
    }

    return FarmerProfile(
      farmerId: requiredString('farmer_id'),
      fullName: requiredString('full_name'),
      village: optionalString('village'),
      mandal: optionalString('mandal'),
      district: optionalString('district'),
      state: optionalString('state'),
      kycStatus: kycStatus,
      payoutStatus: requiredString('payout_status'),
      preferredLanguage: preferredLanguage,
    );
  }
}
