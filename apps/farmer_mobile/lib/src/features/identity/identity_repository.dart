import '../../core/api/api_client.dart';
import '../../core/api/token_store.dart';

class IdentityRepository {
  IdentityRepository(this._api, this._tokenStore);
  final ApiClient _api;
  final TokenStore _tokenStore;

  Future<Map<String, dynamic>> farmerMe() => _api.get('/identity/farmers/me');

  Future<Map<String, dynamic>> registrationStatus() =>
      _api.get('/identity/farmer-registration/status');

  Future<Map<String, dynamic>> saveRegistrationDetails({
    required String fullName,
    required String language,
    String? village,
    String? mandal,
    String? district,
  }) {
    return _api.put('/identity/farmer-registration/details', body: {
      'full_name': fullName,
      'village': village,
      'mandal': mandal,
      'district': district,
      'state': 'Telangana',
      'preferred_language': language,
    });
  }

  Future<Map<String, dynamic>> submitKyc({
    required String aadhaarNumber,
  }) async {
    final json = await _api.post('/identity/farmer-registration/kyc', body: {
      'aadhaar_number': aadhaarNumber,
    });
    await _tokenStore.save(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
    );
    return json;
  }
}
