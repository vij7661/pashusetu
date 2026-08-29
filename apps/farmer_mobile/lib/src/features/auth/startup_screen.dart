import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api/token_store.dart';
import '../../core/providers.dart';
import '../providers.dart';

class StartupScreen extends ConsumerStatefulWidget {
  const StartupScreen({super.key});

  @override
  ConsumerState<StartupScreen> createState() => _StartupScreenState();
}

class _StartupScreenState extends ConsumerState<StartupScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(_resolveSession);
  }

  Future<void> _resolveSession() async {
    final tokenStore = ref.read(tokenStoreProvider);
    final token = await tokenStore.accessToken();
    if (!mounted) return;

    if (token == null || token.isEmpty) {
      context.go('/');
      return;
    }

    final kind = await tokenStore.sessionKind();

    try {
      if (kind == TokenStore.registrationSession) {
        await ref.read(identityRepositoryProvider).registrationStatus();
        if (mounted) context.go('/register?resume=1');
        return;
      }

      if (kind == TokenStore.accountSession) {
        await ref.read(identityRepositoryProvider).farmerMe();
        if (mounted) context.go('/home');
        return;
      }

      // Backward-compatible recovery for tokens saved before session_kind existed.
      try {
        await ref.read(identityRepositoryProvider).farmerMe();
        if (mounted) context.go('/home');
        return;
      } catch (_) {
        await ref.read(identityRepositoryProvider).registrationStatus();
        if (mounted) context.go('/register?resume=1');
        return;
      }
    } catch (_) {
      await tokenStore.clear();
      if (mounted) context.go('/');
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: CircularProgressIndicator()),
    );
  }
}
