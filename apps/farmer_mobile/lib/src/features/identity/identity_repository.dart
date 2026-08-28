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
    required Map<String, dynamic> kyc,
    required Map<String, dynamic> payout,
  }) {
    return _api.post('/identity/farmers', body: {
      'full_name': fullName,
      'village': village,
      'mandal': mandal,
      'district': district,
      'state': 'Telangana',
      'preferred_language': language,
      'kyc': kyc,
      'payout': payout,
    });
  }

  Future<Map<String, dynamic>> verifyKyc({
    required String aadhaarNumber,
    required String name,
    required bool consent,
  }) =>
      _api.post('/identity/farmers/kyc/verify', body: {
        'aadhaar_number': aadhaarNumber,
        'name_as_per_aadhaar': name,
        'consent': consent,
      });
}
