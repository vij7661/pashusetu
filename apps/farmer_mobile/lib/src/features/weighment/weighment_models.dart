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

class WeighmentAcknowledgement {
  const WeighmentAcknowledgement({
    required this.acknowledgementId,
    required this.status,
  });

  final String acknowledgementId;
  final String status;

  factory WeighmentAcknowledgement.fromJson(Map<String, dynamic> json) {
    final id = json['acknowledgement_id'];
    final status = json['status'];
    if (id is! String || id.isEmpty) {
      throw const FormatException('Invalid weighment acknowledgement id');
    }
    if (status != 'ACKNOWLEDGED_BY_FARMER' && status != 'REJECTED_BY_FARMER') {
      throw const FormatException('Invalid weighment acknowledgement status');
    }
    return WeighmentAcknowledgement(
      acknowledgementId: id,
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
