import '../../core/api/api_client.dart';

class IdentityRepository {
  IdentityRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> farmerMe() => _api.get('/identity/farmers/me');

  Future<Map<String, dynamic>> createFarmer({
    required String fullName,
    required String language,
    String? village,
    String? mandal,
    String? district,
  }) {
    return _api.post('/identity/farmers', body: {
      'full_name': fullName,
      'village': village,
      'mandal': mandal,
      'district': district,
      'state': 'Telangana',
      'preferred_language': language,
    });
  }
}
