import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final mobile = TextEditingController(text: '+919876500017');
  final otp = TextEditingController(text: '4816');
  bool sent = false;
  bool busy = false;
  String? error;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(children: [
            const Spacer(),
            const Text('⚖️', style: TextStyle(fontSize: 64)),
            Text('PashuSetu Operator', style: Theme.of(context).textTheme.headlineSmall),
            const Text('Mandal Centre verification'),
            const SizedBox(height: 24),
            TextField(
              controller: mobile,
              decoration: const InputDecoration(labelText: 'Operator mobile'),
            ),
            const SizedBox(height: 10),
            if (sent)
              TextField(
                controller: otp,
                decoration: const InputDecoration(labelText: 'OTP'),
              ),
            if (error != null) Text(error!, style: const TextStyle(color: Colors.red)),
            const Spacer(),
            FilledButton(
              onPressed: busy ? null : () async {
                setState(() {
                  busy = true;
                  error = null;
                });
                try {
                  final repo = ref.read(authRepositoryProvider);
                  if (!sent) {
                    await repo.requestOtp(mobile.text.trim());
                    setState(() => sent = true);
                  } else {
                    await repo.verifyOtp(mobile.text.trim(), otp.text.trim());
                    if (mounted) context.go('/home');
                  }
                } catch (e) {
                  setState(() => error = e.toString());
                } finally {
                  if (mounted) setState(() => busy = false);
                }
              },
              child: Text(sent ? 'Login' : 'Send OTP'),
            ),
          ]),
        ),
      ),
    );
  }
}
