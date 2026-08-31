import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/api/api_client.dart';

void main() {
  test('only authentication failures invalidate saved Farmer session', () {
    expect(
      isAuthenticationFailure(
        const ApiException('TOKEN_INVALID', 'Invalid token', statusCode: 401),
      ),
      isTrue,
    );
    expect(
      isAuthenticationFailure(
        const ApiException('ROLE_FORBIDDEN', 'Forbidden', statusCode: 403),
      ),
      isTrue,
    );
    expect(
      isAuthenticationFailure(
        const ApiException('SERVICE_UNAVAILABLE', 'Try again', statusCode: 503),
      ),
      isFalse,
    );
    expect(isAuthenticationFailure(Exception('network unavailable')), isFalse);
  });
}
