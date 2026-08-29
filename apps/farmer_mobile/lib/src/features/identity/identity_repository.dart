import '../../core/api/api_client.dart';
import '../../core/api/token_store.dart';
import 'farmer_dashboard.dart';
import 'farmer_profile.dart';

class IdentityRepository {
  IdentityRepository(this._api, this._tokenStore);
  final ApiClient _api;
  final TokenStore _tokenStore;

  Future<FarmerProfile> farmerMe() async {
    final json = await _api.get('/identity/farmers/me');
    return FarmerProfile.fromJson(json);
  }

  Future<FarmerDashboard> farmerDashboard() async {
    final json = await _api.get('/identity/farmers/me/dashboard');
    return FarmerDashboard.fromJson(json);
  }

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
