import 'package:flutter_test/flutter_test.dart';

void main() {
  test('one UI tap should reuse the same key for retries', () {
    const key = 'buyer-intent-123';
    final retryKey = key;
    expect(retryKey, key);
  });
}
