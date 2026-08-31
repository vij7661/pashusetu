import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api/api_client.dart';
import '../../core/api/token_store.dart';
import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../core/providers.dart';
import '../providers.dart';

class StartupScreen extends ConsumerStatefulWidget {
  const StartupScreen({super.key});

  @override
  ConsumerState<StartupScreen> createState() => _StartupScreenState();
}

class _StartupScreenState extends ConsumerState<StartupScreen> {
  bool resolving = true;
  bool recoverableFailure = false;

  @override
  void initState() {
    super.initState();
    Future.microtask(_resolveSession);
  }

  Future<void> _resolveSession() async {
    if (!mounted) return;
    setState(() {
      resolving = true;
      recoverableFailure = false;
    });

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
    } catch (error) {
      if (isAuthenticationFailure(error)) {
        await tokenStore.clear();
        if (mounted) context.go('/');
        return;
      }

      if (mounted) {
        setState(() {
          resolving = false;
          recoverableFailure = true;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);

    return Scaffold(
      body: Center(
        child: resolving
            ? const CircularProgressIndicator()
            : recoverableFailure
                ? Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          t('connection_error'),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        FilledButton(
                          onPressed: _resolveSession,
                          child: Text(t('continue')),
                        ),
                      ],
                    ),
                  )
                : const CircularProgressIndicator(),
      ),
    );
  }
}
