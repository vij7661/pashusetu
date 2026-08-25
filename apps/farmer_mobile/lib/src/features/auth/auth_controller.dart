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

  Future<void> requestOtp(String mobile) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repo.requestOtp(mobile));
  }

  Future<void> verifyOtp(String mobile, String otp) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repo.verifyOtp(mobile, otp);
    });
  }
}

final authControllerProvider =
    StateNotifierProvider<AuthController, AsyncValue<void>>(
  (ref) => AuthController(ref.watch(authRepositoryProvider)),
);
