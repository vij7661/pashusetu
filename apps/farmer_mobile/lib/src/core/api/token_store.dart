import 'package:shared_preferences/shared_preferences.dart';

class TokenStore {
  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';
  static const _sessionKindKey = 'session_kind';

  static const accountSession = 'account';
  static const registrationSession = 'registration';

  Future<void> save({
    required String accessToken,
    required String refreshToken,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessKey, accessToken);
    await prefs.setString(_refreshKey, refreshToken);
    await prefs.setString(_sessionKindKey, accountSession);
  }

  Future<void> saveRegistrationToken(String registrationToken) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_accessKey, registrationToken);
    await prefs.remove(_refreshKey);
    await prefs.setString(_sessionKindKey, registrationSession);
  }

  Future<String?> accessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_accessKey);
  }

  Future<String?> sessionKind() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_sessionKindKey);
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessKey);
    await prefs.remove(_refreshKey);
    await prefs.remove(_sessionKindKey);
  }
}
