import '../../core/api/api_client.dart';
import 'weighment_models.dart';

class WeighmentRepository {
  WeighmentRepository(this._api);
  final ApiClient _api;

  Future<WeighmentDecision> decide(
    String weighmentId, {
    required bool acknowledged,
  }) async {
    final json = await _api.post(
      '/weighment/sessions/$weighmentId/acknowledge',
      body: {
        'acknowledged': acknowledged,
        'method': 'APP_CONFIRMATION',
      },
    );
    return WeighmentDecision.fromJson(json);
  }

  Future<WeighmentReceipt> createReceipt(String weighmentId) async {
    final json = await _api.post('/weighment/sessions/$weighmentId/receipt');
    return WeighmentReceipt.fromJson(json);
  }
}
