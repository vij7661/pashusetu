import '../../core/api/api_client.dart';

class WeighmentRepository {
  WeighmentRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> acknowledge(String weighmentId) {
    return _api.post(
      '/weighment/sessions/$weighmentId/acknowledge',
      body: {'acknowledged': true, 'method': 'APP_CONFIRMATION'},
    );
  }

  Future<Map<String, dynamic>> createReceipt(String weighmentId) {
    return _api.post('/weighment/sessions/$weighmentId/receipt');
  }

  Future<Map<String, dynamic>> reject(String weighmentId) {
    return _api.post(
      '/weighment/sessions/$weighmentId/acknowledge',
      body: {'acknowledged': false, 'method': 'APP_CONFIRMATION'},
    );
  }
}
