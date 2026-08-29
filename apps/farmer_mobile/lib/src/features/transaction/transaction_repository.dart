import '../../core/api/api_client.dart';

class TransactionRepository {
  TransactionRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> createFromListing(String listingId) =>
      _api.post('/transaction/from-listing/$listingId');

  Future<Map<String, dynamic>> transaction(String id) =>
      _api.get('/transaction/$id');

  Future<Map<String, dynamic>> settlement(String transactionId) =>
      _api.get('/payments/transactions/$transactionId/settlement');

  Future<Map<String, dynamic>> createAgreement({
    required String transactionId,
    required String pickupPoint,
    required String finalWeighingPoint,
    required double tolerancePercent,
  }) {
    return _api.post('/agreement/transactions/$transactionId', body: {
      'pickup_point': pickupPoint,
      'final_weighing_point': finalWeighingPoint,
      'tolerance_percent': tolerancePercent,
    });
  }

  Future<Map<String, dynamic>> confirmAgreement(
    String transactionId,
    String agreementId,
  ) {
    return _api.post(
      '/agreement/transactions/$transactionId/$agreementId/confirm',
      body: {'confirm': true},
    );
  }

  Future<Map<String, dynamic>> close(String transactionId) =>
      _api.post('/transaction/$transactionId/close');
}
