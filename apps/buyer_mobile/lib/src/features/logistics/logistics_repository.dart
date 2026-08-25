import '../../core/api/api_client.dart';

class LogisticsRepository {
  LogisticsRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> delivery({
    required String transactionId,
    required String deliveryWeighmentId,
    required int goatCount,
  }) =>
      _api.post('/logistics/transactions/$transactionId/delivery', body: {
        'qr_verified': true,
        'goat_count': goatCount,
        'delivery_weighment_id': deliveryWeighmentId,
      });
}
