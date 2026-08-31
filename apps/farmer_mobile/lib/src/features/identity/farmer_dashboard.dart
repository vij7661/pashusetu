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
      return value.trim();
    }

    int requiredNonNegativeInt(String key) {
      final value = json[key];
      if (value is! int || value < 0) {
        throw FormatException('Missing or invalid $key');
      }
      return value;
    }

    final enabled = json['transaction_enabled'];
    if (enabled is! bool) {
      throw const FormatException('Missing or invalid transaction_enabled');
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

    final shouldEnableTransactions = kycStatus == 'KYC_VERIFIED';
    if (enabled != shouldEnableTransactions) {
      throw FormatException(
        'Inconsistent Farmer KYC transaction boundary: $kycStatus/$enabled',
      );
    }

    return FarmerDashboard(
      farmerId: requiredString('farmer_id'),
      kycStatus: kycStatus,
      transactionEnabled: enabled,
      liveListings: requiredNonNegativeInt('live_listings'),
      activeOffers: requiredNonNegativeInt('active_offers'),
      settledAmountPaise: requiredNonNegativeInt('settled_amount_paise'),
    );
  }
}
