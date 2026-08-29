import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'auth_controller.dart';

const farmerOtpLength = 4;

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});
  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final mobile = TextEditingController();
  final otp = TextEditingController();
  bool otpSent = false;

  @override
  void dispose() {
    mobile.dispose();
    otp.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(authControllerProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Existing Farmer Login')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: mobile,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: 'Registered mobile',
                hintText: '+91XXXXXXXXXX',
              ),
            ),
            const SizedBox(height: 12),
            if (otpSent)
              TextField(
                controller: otp,
                keyboardType: TextInputType.number,
                maxLength: farmerOtpLength,
                inputFormatters: [
                  FilteringTextInputFormatter.digitsOnly,
                  LengthLimitingTextInputFormatter(farmerOtpLength),
                ],
                decoration: const InputDecoration(labelText: 'OTP'),
              ),
            const Spacer(),
            if (state.hasError)
              Text(state.error.toString(), style: const TextStyle(color: Colors.red)),
            FilledButton(
              onPressed: state.isLoading
                  ? null
                  : () async {
                      final c = ref.read(authControllerProvider.notifier);
                      if (!otpSent) {
                        await c.requestLoginOtp(mobile.text.trim());
                        if (mounted && !ref.read(authControllerProvider).hasError) {
                          setState(() => otpSent = true);
                        }
                      } else {
                        if (otp.text.trim().length != farmerOtpLength) return;
                        await c.verifyLoginOtp(mobile.text.trim(), otp.text.trim());
                        if (!context.mounted) return;
                        if (!ref.read(authControllerProvider).hasError) {
                          context.go('/home');
                        }
                      }
                    },
              child: Text(otpSent ? 'Login & Go to Home' : 'Send OTP'),
            ),
          ],
        ),
      ),
    );
  }
}
