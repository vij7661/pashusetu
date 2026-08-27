import 'package:dio/dio.dart';

import '../../core/api/api_client.dart';
import '../../core/localization/app_strings.dart';

String authErrorMessage(Object error, String language) {
  final apiError = switch (error) {
    ApiException value => value,
    DioException(error: final ApiException value) => value,
    _ => null,
  };

  if (error is DioException &&
      (error.type == DioExceptionType.connectionTimeout ||
          error.type == DioExceptionType.sendTimeout ||
          error.type == DioExceptionType.receiveTimeout ||
          error.type == DioExceptionType.connectionError)) {
    return AppStrings.tr(language, 'connection_error');
  }

  final statusCode = apiError?.statusCode ??
      (error is DioException ? error.response?.statusCode : null);
  final key = switch (apiError?.code) {
    'OTP_INVALID' => 'auth_invalid_otp',
    'OTP_EXPIRED' => 'auth_expired_otp',
    'OTP_NOT_FOUND' => 'auth_no_active_otp',
    'OTP_ATTEMPTS_EXCEEDED' => 'auth_too_many_attempts',
    'QA_TEST_USER_NOT_FOUND' => 'auth_qa_user_not_found',
    'OTP_PROVIDER_UNAVAILABLE' => 'auth_service_unavailable',
    _ when (statusCode ?? 0) >= 500 => 'auth_server_error',
    _ when statusCode != null => 'auth_request_failed',
    _ when apiError != null => 'auth_request_failed',
    _ => 'auth_unknown_error',
  };
  return AppStrings.tr(language, key);
}
