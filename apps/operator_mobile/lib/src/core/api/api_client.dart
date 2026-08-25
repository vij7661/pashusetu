import 'package:dio/dio.dart';

import 'api_config.dart';
import 'token_store.dart';

class ApiClient {
  ApiClient(this._store)
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
          final token = await _store.accessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
      ),
    );
  }

  final TokenStore _store;
  final Dio _dio;

  Future<Map<String, dynamic>> get(String path) async =>
      (await _dio.get<Map<String, dynamic>>(path)).data ?? {};

  Future<Map<String, dynamic>> post(
    String path, {
    Map<String, dynamic>? body,
    Map<String, dynamic>? headers,
  }) async =>
      (await _dio.post<Map<String, dynamic>>(
        path,
        data: body,
        options: Options(headers: headers),
      ))
          .data ??
      {};
}
