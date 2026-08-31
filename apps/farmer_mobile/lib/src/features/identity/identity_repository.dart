import '../../core/api/api_client.dart';
import '../../core/api/token_store.dart';
import 'farmer_dashboard.dart';
import 'farmer_profile.dart';
import 'farmer_registration.dart';

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

  Future<FarmerRegistrationStatus> registrationStatus() async {
    final json = await _api.get('/identity/farmer-registration/status');
    return FarmerRegistrationStatus.fromJson(json);
  }

  Future<FarmerRegistrationStatus> saveRegistrationDetails({
    required String fullName,
    required String language,
    String? village,
    String? mandal,
    String? district,
  }) async {
    final json = await _api.put('/identity/farmer-registration/details', body: {
      'full_name': fullName,
      'village': village,
      'mandal': mandal,
      'district': district,
      'preferred_language': language,
    });
    return FarmerRegistrationStatus.fromJson(json);
  }

  Future<FarmerRegistrationComplete> submitKyc({
    required String aadhaarNumber,
  }) async {
    final json = await _api.post('/identity/farmer-registration/kyc', body: {
      'aadhaar_number': aadhaarNumber,
    });
    final result = FarmerRegistrationComplete.fromJson(json);
    await _tokenStore.save(
      accessToken: result.accessToken,
      refreshToken: result.refreshToken,
    );
    return result;
  }
}
