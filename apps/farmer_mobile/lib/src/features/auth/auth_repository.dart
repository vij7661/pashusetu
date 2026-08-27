import '../../core/api/api_client.dart';
import '../../core/api/token_store.dart';
import 'auth_models.dart';
import 'mobile_number.dart';

class AuthRepository {
  AuthRepository(this._api, this._tokenStore);
  final ApiClient _api;
  final TokenStore _tokenStore;

  Future<void> requestOtp(String mobile) async {
    await _api.post('/auth/otp/request', body: {
      'mobile_e164': toIndiaE164(mobile),
      'purpose': 'LOGIN',
    });
  }

  Future<TokenPair> verifyOtp(String mobile, String otp) async {
    final json = await _api.post('/auth/otp/verify', body: {
      'mobile_e164': toIndiaE164(mobile),
      'otp': otp,
      'purpose': 'LOGIN',
    });
    final pair = TokenPair.fromJson(json);
    await _tokenStore.save(
      accessToken: pair.accessToken,
      refreshToken: pair.refreshToken,
    );
    return pair;
  }

  Future<Map<String, dynamic>> me() => _api.get('/auth/me');

  Future<void> logout() => _tokenStore.clear();
}
