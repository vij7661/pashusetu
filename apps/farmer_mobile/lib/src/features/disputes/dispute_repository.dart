import '../../core/api/api_client.dart';
import 'dispute_models.dart';

class DisputeRepository {
  DisputeRepository(this._api);
  final ApiClient _api;

  Future<DisputeView> open({
    required String transactionId,
    required String reason,
    required int disputedAmountPaise,
  }) async {
    final json = await _api.post('/disputes/transactions/$transactionId', body: {
      'reason': reason,
      'disputed_amount_paise': disputedAmountPaise,
    });
    return DisputeView.fromJson(json);
  }
}
