import '../../core/api/api_client.dart';

class DisputeRepository {
  DisputeRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> open({
    required String transactionId,
    required String reason,
    required int disputedAmountPaise,
  }) =>
      _api.post('/disputes/transactions/$transactionId', body: {
        'reason': reason,
        'disputed_amount_paise': disputedAmountPaise,
      });
}
