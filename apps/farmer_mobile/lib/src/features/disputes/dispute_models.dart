class DisputeView {
  const DisputeView({
    required this.id,
    required this.transactionId,
    required this.reason,
    required this.disputedAmountPaise,
    required this.status,
    required this.settlementAdjustmentPaise,
    required this.finalDecision,
  });

  final String id;
  final String transactionId;
  final String reason;
  final int disputedAmountPaise;
  final String status;
  final int settlementAdjustmentPaise;
  final String? finalDecision;

  factory DisputeView.fromJson(Map<String, dynamic> json) {
    return DisputeView(
      id: _requiredString(json, 'dispute_id'),
      transactionId: _requiredString(json, 'transaction_id'),
      reason: _requiredString(json, 'reason'),
      disputedAmountPaise: _requiredInt(json, 'disputed_amount_paise'),
      status: _requiredString(json, 'status'),
      settlementAdjustmentPaise: _requiredInt(json, 'settlement_adjustment_paise'),
      finalDecision: _optionalString(json, 'final_decision'),
    );
  }
}

class DisputeEvidenceView {
  const DisputeEvidenceView({required this.id, required this.status});

  final String id;
  final String status;

  factory DisputeEvidenceView.fromJson(Map<String, dynamic> json) {
    return DisputeEvidenceView(
      id: _requiredString(json, 'evidence_id'),
      status: _requiredString(json, 'status'),
    );
  }
}

class DisputeReweighView {
  const DisputeReweighView({
    required this.id,
    required this.stage,
    required this.status,
  });

  final String id;
  final String stage;
  final String status;

  factory DisputeReweighView.fromJson(Map<String, dynamic> json) {
    return DisputeReweighView(
      id: _requiredString(json, 'reweigh_id'),
      stage: _requiredString(json, 'stage'),
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
