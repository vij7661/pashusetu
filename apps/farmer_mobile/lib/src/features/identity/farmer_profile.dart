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
      return value;
    }

    String? optionalString(String key) {
      final value = json[key];
      if (value == null) return null;
      if (value is! String) throw FormatException('Invalid $key');
      final trimmed = value.trim();
      return trimmed.isEmpty ? null : trimmed;
    }

    return FarmerProfile(
      farmerId: requiredString('farmer_id'),
      fullName: requiredString('full_name'),
      village: optionalString('village'),
      mandal: optionalString('mandal'),
      district: optionalString('district'),
      state: optionalString('state'),
      kycStatus: requiredString('kyc_status'),
      payoutStatus: requiredString('payout_status'),
      preferredLanguage: requiredString('preferred_language'),
    );
  }
}
