import '../../core/api/api_client.dart';
import '../../core/api/token_store.dart';
import 'auth_models.dart';

class AuthRepository {
  AuthRepository(this._api, this._tokenStore);
  final ApiClient _api;
  final TokenStore _tokenStore;

  Future<void> requestLoginOtp(String mobile) async {
    await _api.post('/auth/otp/request', body: {
      'mobile_e164': mobile,
      'purpose': 'FARMER_LOGIN',
    });
  }

  Future<TokenPair> verifyLoginOtp(String mobile, String otp) async {
    final json = await _api.post('/auth/otp/verify', body: {
      'mobile_e164': mobile,
      'otp': otp,
      'purpose': 'FARMER_LOGIN',
    });
    final pair = TokenPair.fromJson(json);
    await _tokenStore.save(
      accessToken: pair.accessToken,
      refreshToken: pair.refreshToken,
    );
    return pair;
  }

  Future<void> requestRegistrationOtp(String mobile) async {
    await _api.post('/auth/farmer-registration/otp/request', body: {
      'mobile_e164': mobile,
      'purpose': 'FARMER_REGISTRATION',
    });
  }

  Future<FarmerRegistrationSession> verifyRegistrationOtp(
    String mobile,
    String otp,
  ) async {
    final json = await _api.post('/auth/farmer-registration/otp/verify', body: {
      'mobile_e164': mobile,
      'otp': otp,
      'purpose': 'FARMER_REGISTRATION',
    });
    final session = FarmerRegistrationSession.fromJson(json);
    await _tokenStore.saveRegistrationToken(session.registrationToken);
    return session;
  }

  Future<Map<String, dynamic>> me() => _api.get('/auth/me');

  Future<void> logout() => _tokenStore.clear();
}
