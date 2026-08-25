import '../../core/api/api_client.dart';

class BuyerRepository {
  BuyerRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> createBuyer({
    required String businessName,
    required String buyerType,
    required String language,
    String? contactPerson,
    String? city,
  }) =>
      _api.post('/identity/buyers', body: {
        'business_name': businessName,
        'contact_person': contactPerson,
        'buyer_type': buyerType,
        'city': city,
        'state': 'Telangana',
        'preferred_language': language,
      });

  Future<Map<String, dynamic>> me() => _api.get('/identity/buyers/me');
}
