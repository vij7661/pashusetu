import 'package:dio/dio.dart';

import 'api_config.dart';
import 'token_store.dart';

class ApiException implements Exception {
  const ApiException(this.code, this.message, {this.statusCode});
  final String code;
  final String message;
  final int? statusCode;

  @override
  String toString() => '$code: $message';
}

class ApiClient {
  ApiClient(this._tokenStore)
      : _dio = Dio(
          BaseOptions(
            baseUrl: ApiConfig.baseUrl,
            connectTimeout: const Duration(seconds: 15),
            receiveTimeout: const Duration(seconds: 20),
            headers: {'Content-Type': 'application/json'},
          ),
        ) {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _tokenStore.accessToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) {
          final data = error.response?.data;
          if (data is Map<String, dynamic>) {
            handler.reject(
              DioException(
                requestOptions: error.requestOptions,
                response: error.response,
                type: error.type,
                error: ApiException(
                  data['code']?.toString() ?? 'API_ERROR',
                  data['message']?.toString() ?? 'Something went wrong.',
                  statusCode: error.response?.statusCode,
                ),
              ),
            );
            return;
          }
          handler.next(error);
        },
      ),
    );
  }

  final Dio _dio;
  final TokenStore _tokenStore;

  Future<Map<String, dynamic>> get(String path, {Map<String, dynamic>? query}) async {
    final response = await _dio.get<Map<String, dynamic>>(path, queryParameters: query);
    return response.data ?? {};
  }

  Future<List<dynamic>> getList(String path, {Map<String, dynamic>? query}) async {
    final response = await _dio.get<List<dynamic>>(path, queryParameters: query);
    return response.data ?? const [];
  }

  Future<Map<String, dynamic>> post(
    String path, {
    Map<String, dynamic>? body,
    Map<String, dynamic>? headers,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      path,
      data: body,
      options: Options(headers: headers),
    );
    return response.data ?? {};
  }

  Future<Map<String, dynamic>> put(
    String path, {
    Map<String, dynamic>? body,
    Map<String, dynamic>? headers,
  }) async {
    final response = await _dio.put<Map<String, dynamic>>(
      path,
      data: body,
      options: Options(headers: headers),
    );
    return response.data ?? {};
  }
}
