import '../../core/api/api_client.dart';

class TransactionRepository {
  TransactionRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> createFromListing(String listingId) =>
      _api.post('/transaction/from-listing/$listingId');

  Future<Map<String, dynamic>> getTransaction(String transactionId) =>
      _api.get('/transaction/$transactionId');

  Future<Map<String, dynamic>> activeAgreement(String transactionId) =>
      _api.get('/agreement/transactions/$transactionId/active');

  Future<Map<String, dynamic>> confirmAgreement(String transactionId, String agreementId) =>
      _api.post(
        '/agreement/transactions/$transactionId/$agreementId/confirm',
        body: {'confirm': true},
      );

  Future<Map<String, dynamic>> secureFunds(String transactionId) =>
      _api.post('/payments/transactions/$transactionId/secure');

  Future<Map<String, dynamic>> settle(String transactionId) =>
      _api.post('/payments/transactions/$transactionId/settle');
}
