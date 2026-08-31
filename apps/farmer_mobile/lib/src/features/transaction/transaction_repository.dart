import '../../core/api/api_client.dart';
import 'transaction_models.dart';

class TransactionRepository {
  TransactionRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> createFromListing(String listingId) =>
      _api.post('/transaction/from-listing/$listingId');

  Future<TransactionView> transaction(String id) async {
    final json = await _api.get('/transaction/$id');
    return TransactionView.fromJson(json);
  }

  Future<SettlementView> settlement(String transactionId) async {
    final json = await _api.get('/payments/transactions/$transactionId/settlement');
    return SettlementView.fromJson(json);
  }

  Future<AgreementView> createAgreement({
    required String transactionId,
    required String pickupPoint,
    required String finalWeighingPoint,
    required double tolerancePercent,
  }) async {
    final json = await _api.post('/agreement/transactions/$transactionId', body: {
      'pickup_point': pickupPoint,
      'final_weighing_point': finalWeighingPoint,
      'tolerance_percent': tolerancePercent,
    });
    return AgreementView.fromJson(json);
  }

  Future<AgreementView> confirmAgreement(
    String transactionId,
    String agreementId,
  ) async {
    final json = await _api.post(
      '/agreement/transactions/$transactionId/$agreementId/confirm',
      body: {'confirm': true},
    );
    return AgreementView.fromJson(json);
  }
}
