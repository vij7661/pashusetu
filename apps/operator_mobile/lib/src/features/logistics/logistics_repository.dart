import '../../core/api/api_client.dart';

class LogisticsRepository {
  LogisticsRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> pickup({
    required String transactionId,
    required int goatCount,
    required String loadingVideoEvidenceId,
    required String idempotencyKey,
  }) {
    return _api.post('/logistics/transactions/$transactionId/pickup', body: {
      'qr_verified': true,
      'goat_count': goatCount,
      'loading_video_evidence_id': loadingVideoEvidenceId,
      'departure_note': 'Operator verified departure',
      'idempotency_key': idempotencyKey,
    });
  }

  Future<Map<String, dynamic>> delivery({
    required String transactionId,
    required String deliveryWeighmentId,
    required int goatCount,
    required String deliveryVideoEvidenceId,
    required String idempotencyKey,
  }) {
    return _api.post('/logistics/transactions/$transactionId/delivery', body: {
      'qr_verified': true,
      'goat_count': goatCount,
      'delivery_video_evidence_id': deliveryVideoEvidenceId,
      'delivery_weighment_id': deliveryWeighmentId,
      'idempotency_key': idempotencyKey,
    });
  }
}
