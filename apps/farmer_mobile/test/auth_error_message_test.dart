import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/api/api_client.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_error_message.dart';

DioException _dioError({
  ApiException? apiError,
  DioExceptionType type = DioExceptionType.badResponse,
  int? statusCode,
}) {
  final request = RequestOptions(path: '/auth/otp/verify');
  return DioException(
    requestOptions: request,
    type: type,
    error: apiError,
    response: statusCode == null
        ? null
        : Response(requestOptions: request, statusCode: statusCode),
  );
}

void main() {
  const cases = {
    'OTP_INVALID': (
      'The OTP is incorrect. Please try again.',
      'OTP తప్పుగా ఉంది. మళ్లీ ప్రయత్నించండి.',
    ),
    'OTP_EXPIRED': (
      'The OTP has expired. Request a new OTP.',
      'OTP గడువు ముగిసింది. కొత్త OTP కోరండి.',
    ),
    'OTP_NOT_FOUND': (
      'No active OTP. Request a new OTP.',
      'సక్రియ OTP లేదు. కొత్త OTP కోరండి.',
    ),
    'OTP_ATTEMPTS_EXCEEDED': (
      'Too many attempts. Request a new OTP.',
      'చాలా ప్రయత్నాలు చేశారు. కొత్త OTP కోరండి.',
    ),
    'QA_TEST_USER_NOT_FOUND': (
      'This mobile number is not registered for QA testing.',
      'ఈ మొబైల్ నంబర్ QA పరీక్ష కోసం నమోదు కాలేదు.',
    ),
    'OTP_PROVIDER_UNAVAILABLE': (
      'OTP service is unavailable. Please try again later.',
      'OTP సేవ అందుబాటులో లేదు. తరువాత మళ్లీ ప్రయత్నించండి.',
    ),
  };

  test('auth domain errors map to localized non-technical messages', () {
    for (final entry in cases.entries) {
      final error = _dioError(
        apiError: ApiException(entry.key, 'raw backend message'),
      );
      expect(authErrorMessage(error, 'en'), entry.value.$1);
      expect(authErrorMessage(error, 'te'), entry.value.$2);
    }
  });

  test('network server client and unknown failures are friendly', () {
    final messages = [
      authErrorMessage(
        _dioError(type: DioExceptionType.connectionTimeout),
        'en',
      ),
      authErrorMessage(_dioError(statusCode: 500), 'en'),
      authErrorMessage(_dioError(statusCode: 400), 'en'),
      authErrorMessage(StateError('stack detail'), 'en'),
    ];
    expect(messages, [
      'Unable to connect to PashuSetu. Please check the backend connection and try again.',
      'Server error. Please try again later.',
      'Unable to complete the request. Check your details.',
      'Something went wrong. Please try again.',
    ]);
    for (final message in messages) {
      expect(message, isNot(contains('DioException')));
      expect(message, isNot(contains('OTP_')));
      expect(message, isNot(contains('StateError')));
      expect(message, isNot(contains('{')));
    }
  });
}
