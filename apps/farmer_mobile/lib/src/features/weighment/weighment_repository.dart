import '../../core/api/api_client.dart';

class WeighmentRepository {
  WeighmentRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> review(String weighmentId) {
    return _api.get('/weighment/sessions/$weighmentId/farmer-review');
  }

  Future<Map<String, dynamic>> acknowledge(
    String weighmentId, {
    required bool acknowledged,
  }) {
    return _api.post(
      '/weighment/sessions/$weighmentId/acknowledge',
      body: {
        'acknowledged': acknowledged,
        'method': 'APP_CONFIRMATION',
      },
    );
  }

  Future<Map<String, dynamic>> createReceipt(String weighmentId) {
    return _api.post('/weighment/sessions/$weighmentId/receipt');
  }
}
