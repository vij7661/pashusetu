class TransactionView {
  const TransactionView({
    required this.id,
    required this.listingId,
    required this.acceptedBidId,
    required this.state,
    required this.activeAgreementId,
  });

  final String id;
  final String listingId;
  final String acceptedBidId;
  final String state;
  final String? activeAgreementId;

  factory TransactionView.fromJson(Map<String, dynamic> json) {
    return TransactionView(
      id: _requiredString(json, 'transaction_id'),
      listingId: _requiredString(json, 'listing_id'),
      acceptedBidId: _requiredString(json, 'accepted_bid_id'),
      state: _requiredString(json, 'state'),
      activeAgreementId: _optionalString(json, 'active_agreement_id'),
    );
  }
}

class SettlementView {
  const SettlementView({
    required this.id,
    required this.grossAmountPaise,
    required this.adjustmentPaise,
    required this.platformFeePaise,
    required this.finalAmountPaise,
    required this.status,
  });

  final String id;
  final int grossAmountPaise;
  final int adjustmentPaise;
  final int platformFeePaise;
  final int finalAmountPaise;
  final String status;

  factory SettlementView.fromJson(Map<String, dynamic> json) {
    return SettlementView(
      id: _requiredString(json, 'settlement_id'),
      grossAmountPaise: _requiredInt(json, 'gross_amount_paise'),
      adjustmentPaise: _requiredInt(json, 'adjustment_paise'),
      platformFeePaise: _requiredInt(json, 'platform_fee_paise'),
      finalAmountPaise: _requiredInt(json, 'final_amount_paise'),
      status: _requiredString(json, 'status'),
    );
  }
}

String _requiredString(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is! String || value.trim().isEmpty) {
    throw FormatException('Missing or invalid $key');
  }
  return value;
}

String? _optionalString(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value == null) return null;
  if (value is! String || value.trim().isEmpty) {
    throw FormatException('Invalid $key');
  }
  return value;
}

int _requiredInt(Map<String, dynamic> json, String key) {
  final value = json[key];
  if (value is! int) {
    throw FormatException('Missing or invalid $key');
  }
  return value;
}
