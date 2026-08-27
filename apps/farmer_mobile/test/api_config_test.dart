import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/api/api_config.dart';

void main() {
  test('uses localhost for Flutter Web development', () {
    expect(
      ApiConfig.resolve(isWeb: true, override: ''),
      'http://localhost:8000/api/v1',
    );
  });

  test('uses the Android emulator host alias outside Web', () {
    expect(
      ApiConfig.resolve(isWeb: false, override: ''),
      'http://10.0.2.2:8000/api/v1',
    );
  });

  test('honors an explicit API base URL override', () {
    expect(
      ApiConfig.resolve(
        isWeb: true,
        override: 'http://dev.example.test/api/v1',
      ),
      'http://dev.example.test/api/v1',
    );
  });
}
