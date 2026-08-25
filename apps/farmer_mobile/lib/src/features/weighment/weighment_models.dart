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
