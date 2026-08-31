import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers.dart';
import 'auth_repository.dart';

final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => AuthRepository(
    ref.watch(apiClientProvider),
    ref.watch(tokenStoreProvider),
  ),
);

class AuthController extends StateNotifier<AsyncValue<void>> {
  AuthController(this._repo) : super(const AsyncData(null));
  final AuthRepository _repo;

  Future<void> requestLoginOtp(String mobile) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repo.requestLoginOtp(mobile));
  }

  Future<void> verifyLoginOtp(String mobile, String otp) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repo.verifyLoginOtp(mobile, otp);
    });
  }

  Future<void> requestRegistrationOtp(String mobile) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repo.requestRegistrationOtp(mobile));
  }

  Future<Map<String, dynamic>?> verifyRegistrationOtp(
    String mobile,
    String otp,
  ) async {
    Map<String, dynamic>? result;
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      result = await _repo.verifyRegistrationOtp(mobile, otp);
    });
    return result;
  }
}

final authControllerProvider =
    StateNotifierProvider<AuthController, AsyncValue<void>>(
  (ref) => AuthController(ref.watch(authRepositoryProvider)),
);
