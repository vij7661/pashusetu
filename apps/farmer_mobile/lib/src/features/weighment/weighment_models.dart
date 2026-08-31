class WeighmentView {
  WeighmentView({
    required this.id,
    required this.targetType,
    required this.targetId,
    required this.status,
    required this.scaleCode,
    required this.centreCode,
  });

  final String id;
  final String targetType;
  final String targetId;
  final String status;
  final String scaleCode;
  final String centreCode;

  factory WeighmentView.fromJson(Map<String, dynamic> json) => WeighmentView(
        id: json['weighment_id'] as String,
        targetType: json['target_type'] as String,
        targetId: json['target_id'].toString(),
        status: json['status'] as String,
        scaleCode: json['scale_code'] as String,
        centreCode: json['centre_code'] as String,
      );
}

class WeighmentDecision {
  const WeighmentDecision({
    required this.status,
    this.acknowledgementId,
  });

  final String? acknowledgementId;
  final String status;

  bool get accepted => status == 'ACKNOWLEDGED';
  bool get rejected => status == 'REJECTED_BY_FARMER';

  factory WeighmentDecision.fromJson(Map<String, dynamic> json) {
    final status = json['status'];
    if (status != 'ACKNOWLEDGED' && status != 'REJECTED_BY_FARMER') {
      throw const FormatException('Invalid weighment decision status');
    }
    final rawId = json['acknowledgement_id'];
    if (rawId != null && (rawId is! String || rawId.isEmpty)) {
      throw const FormatException('Invalid weighment acknowledgement id');
    }
    if (status == 'ACKNOWLEDGED' && rawId == null) {
      throw const FormatException('Acknowledged weighment requires acknowledgement id');
    }
    if (status == 'REJECTED_BY_FARMER' && rawId != null) {
      throw const FormatException('Rejected weighment must not have acknowledgement id');
    }
    return WeighmentDecision(
      acknowledgementId: rawId as String?,
      status: status as String,
    );
  }
}

class WeighmentReceipt {
  WeighmentReceipt({
    required this.receiptId,
    required this.receiptCode,
    required this.printStatus,
    required this.targetType,
    required this.targetId,
  });

  final String receiptId;
  final String receiptCode;
  final String printStatus;
  final String targetType;
  final String targetId;

  factory WeighmentReceipt.fromJson(Map<String, dynamic> json) {
    final targetType = json['target_type'] as String;
    if (targetType != 'GOAT' && targetType != 'LOT') {
      throw const FormatException('Invalid weighment receipt target type');
    }
    return WeighmentReceipt(
      receiptId: json['receipt_id'] as String,
      receiptCode: json['receipt_code'] as String,
      printStatus: json['print_status'] as String,
      targetType: targetType,
      targetId: json['target_id'] as String,
    );
  }
}
