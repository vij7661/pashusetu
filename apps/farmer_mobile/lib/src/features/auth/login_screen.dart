import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'auth_controller.dart';
import 'auth_error_message.dart';
import 'mobile_number.dart';
import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});
  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final mobile = TextEditingController();
  final otp = TextEditingController();
  bool otpSent = false;
  String? localError;

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(authControllerProvider);
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);
    return Scaffold(
      appBar: AppBar(title: Text(t('existing_farmer_login'))),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
                controller: mobile,
                keyboardType: TextInputType.phone,
                inputFormatters: const [MobileNumberInputFormatter()],
                autofillHints: const <String>[],
                autocorrect: false,
                enableSuggestions: false,
                decoration: InputDecoration(labelText: t('registered_mobile'))),
            const SizedBox(height: 12),
            if (otpSent)
              TextField(
                  controller: otp,
                  keyboardType: TextInputType.number,
                  inputFormatters: const [OtpInputFormatter()],
                  autofillHints: const <String>[],
                  decoration: InputDecoration(labelText: t('otp'))),
            const Spacer(),
            if (localError != null)
              Text(localError!, style: const TextStyle(color: Colors.red)),
            if (state.hasError)
              Text(authErrorMessage(state.error!, language),
                  style: const TextStyle(color: Colors.red)),
            FilledButton(
              onPressed: state.isLoading
                  ? null
                  : () async {
                      final c = ref.read(authControllerProvider.notifier);
                      setState(() => localError = null);
                      if (!otpSent) {
                        if (!isValidMobileNumber(mobile.text)) {
                          setState(
                            () => localError = t('invalid_mobile_number'),
                          );
                          return;
                        }
                        await c.requestOtp(mobile.text.trim());
                        if (mounted &&
                            !ref.read(authControllerProvider).hasError) {
                          setState(() => otpSent = true);
                        }
                      } else {
                        if (!isValidOtp(otp.text)) {
                          setState(() => localError = t('invalid_otp'));
                          return;
                        }
                        await c.verifyOtp(mobile.text.trim(), otp.text.trim());
                        if (!context.mounted) return;
                        if (!ref.read(authControllerProvider).hasError) {
                          context.go('/home');
                        }
                      }
                    },
              child: Text(otpSent ? t('login_go_home') : t('send_otp')),
            ),
          ],
        ),
      ),
    );
  }
}
