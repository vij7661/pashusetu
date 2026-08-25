import '../../core/api/api_client.dart';
import '../../core/api/token_store.dart';

class AuthRepository {
  AuthRepository(this._api, this._store);
  final ApiClient _api;
  final TokenStore _store;

  Future<void> requestOtp(String mobile) async {
    await _api.post('/auth/otp/request', body: {
      'mobile_e164': mobile,
      'purpose': 'LOGIN',
    });
  }

  Future<void> verifyOtp(String mobile, String otp) async {
    final x = await _api.post('/auth/otp/verify', body: {
      'mobile_e164': mobile,
      'otp': otp,
      'purpose': 'LOGIN',
    });
    await _store.save(
      x['access_token'] as String,
      x['refresh_token'] as String,
    );
  }
}
