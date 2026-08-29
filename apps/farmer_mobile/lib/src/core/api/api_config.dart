import 'package:flutter/foundation.dart';

class ApiConfig {
  static const _override = String.fromEnvironment('API_BASE_URL');

  static String resolve({required bool isWeb, String override = _override}) {
    if (override.isNotEmpty) return override;
    if (isWeb) return 'http://localhost:8000/api/v1';
    return 'http://10.0.2.2:8000/api/v1';
  }

  static String get baseUrl => resolve(isWeb: kIsWeb);
}
