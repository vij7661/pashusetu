class FarmerDashboard {
  const FarmerDashboard({
    required this.farmerId,
    required this.kycStatus,
    required this.transactionEnabled,
    required this.liveListings,
    required this.activeOffers,
    required this.settledAmountPaise,
  });

  final String farmerId;
  final String kycStatus;
  final bool transactionEnabled;
  final int liveListings;
  final int activeOffers;
  final int settledAmountPaise;

  factory FarmerDashboard.fromJson(Map<String, dynamic> json) {
    String requiredString(String key) {
      final value = json[key];
      if (value is! String || value.trim().isEmpty) {
        throw FormatException('Missing or invalid $key');
      }
      return value;
    }

    int requiredInt(String key) {
      final value = json[key];
      if (value is! int) {
        throw FormatException('Missing or invalid $key');
      }
      return value;
    }

    final enabled = json['transaction_enabled'];
    if (enabled is! bool) {
      throw const FormatException('Missing or invalid transaction_enabled');
    }

    return FarmerDashboard(
      farmerId: requiredString('farmer_id'),
      kycStatus: requiredString('kyc_status'),
      transactionEnabled: enabled,
      liveListings: requiredInt('live_listings'),
      activeOffers: requiredInt('active_offers'),
      settledAmountPaise: requiredInt('settled_amount_paise'),
    );
  }
}
