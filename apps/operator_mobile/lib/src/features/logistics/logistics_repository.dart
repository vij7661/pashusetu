import '../../core/api/api_client.dart';

class LogisticsRepository {
  LogisticsRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> pickup({
    required String transactionId,
    required int goatCount,
    String? loadingVideoEvidenceId,
  }) {
    return _api.post('/logistics/transactions/$transactionId/pickup', body: {
      'qr_verified': true,
      'goat_count': goatCount,
      'loading_video_evidence_id': loadingVideoEvidenceId,
      'departure_note': 'Operator verified departure',
    });
  }
}
