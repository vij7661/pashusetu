import 'package:shared_preferences/shared_preferences.dart';

class TokenStore {
  static const _access = 'access_token';
  static const _refresh = 'refresh_token';

  Future<void> save(String access, String refresh) async {
    final p = await SharedPreferences.getInstance();
    await p.setString(_access, access);
    await p.setString(_refresh, refresh);
  }

  Future<String?> accessToken() async {
    final p = await SharedPreferences.getInstance();
    return p.getString(_access);
  }

  Future<void> clear() async {
    final p = await SharedPreferences.getInstance();
    await p.remove(_access);
    await p.remove(_refresh);
  }
}
