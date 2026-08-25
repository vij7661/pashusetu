import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../auth/auth_controller.dart';
import '../providers.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  int step = 0;
  final mobile = TextEditingController(text: '+919876543210');
  final otp = TextEditingController(text: '4816');
  final name = TextEditingController(text: 'Ramesh');
  final village = TextEditingController(text: 'Chityal');
  final mandal = TextEditingController(text: 'Chityal');
  final district = TextEditingController(text: 'Nalgonda');
  final aadhaar = TextEditingController();
  final upi = TextEditingController();
  String language = 'te';
  bool busy = false;
  String? error;

  Future<void> next() async {
    setState(() { busy = true; error = null; });
    try {
      if (step == 0) {
        await ref.read(authControllerProvider.notifier).requestOtp(mobile.text.trim());
      } else if (step == 1) {
        await ref.read(authControllerProvider.notifier).verifyOtp(mobile.text.trim(), otp.text.trim());
      } else if (step == 5) {
        await ref.read(identityRepositoryProvider).createFarmer(
          fullName: name.text.trim(),
          language: language,
          village: village.text.trim(),
          mandal: mandal.text.trim(),
          district: district.text.trim(),
        );
      }
      if (!mounted) return;
      if (step >= 6) {
        context.go('/home');
      } else {
        setState(() => step++);
      }
    } catch (e) {
      setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final titles = [
      'Mobile Verification',
      'Enter OTP',
      'Choose Language',
      'Farmer Details',
      'KYC Verification',
      'Payout Setup',
      'Review Registration',
    ];

    Widget content;
    switch (step) {
      case 0:
        content = TextField(controller: mobile, decoration: const InputDecoration(labelText: 'Mobile number'));
      case 1:
        content = TextField(controller: otp, decoration: const InputDecoration(labelText: 'OTP'));
      case 2:
        content = DropdownButtonFormField<String>(
          initialValue: language,
          items: const [
            DropdownMenuItem(value: 'te', child: Text('తెలుగు')),
            DropdownMenuItem(value: 'hi', child: Text('हिंदी')),
            DropdownMenuItem(value: 'en', child: Text('English')),
            DropdownMenuItem(value: 'mr', child: Text('मराठी')),
            DropdownMenuItem(value: 'ta', child: Text('தமிழ்')),
            DropdownMenuItem(value: 'ml', child: Text('മലയാളം')),
          ],
          onChanged: (v) => setState(() => language = v ?? 'te'),
        );
      case 3:
        content = Column(children: [
          TextField(controller: name, decoration: const InputDecoration(labelText: 'Full name')),
          const SizedBox(height: 10),
          TextField(controller: village, decoration: const InputDecoration(labelText: 'Village')),
          const SizedBox(height: 10),
          TextField(controller: mandal, decoration: const InputDecoration(labelText: 'Mandal')),
          const SizedBox(height: 10),
          TextField(controller: district, decoration: const InputDecoration(labelText: 'District')),
        ]);
      case 4:
        content = Column(children: [
          TextField(controller: aadhaar, decoration: const InputDecoration(labelText: '12-digit Aadhaar number')),
          const SizedBox(height: 10),
          const Text(
            'UI only in APP-1. The backend intentionally does not store raw Aadhaar. '
            'This screen will connect to the selected KYC provider adapter later.',
          ),
        ]);
      case 5:
        content = Column(children: [
          TextField(controller: upi, decoration: const InputDecoration(labelText: 'UPI ID or Bank Account')),
          const SizedBox(height: 10),
          const Text('Payout details are collected only during new registration.'),
        ]);
      default:
        content = const Text(
          'Review your information. Farmer profile is created in the backend when you continue.',
        );
    }

    return Scaffold(
      appBar: AppBar(title: Text(titles[step])),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            LinearProgressIndicator(value: (step + 1) / titles.length),
            const SizedBox(height: 20),
            Expanded(child: SingleChildScrollView(child: content)),
            if (error != null) Text(error!, style: const TextStyle(color: Colors.red)),
            FilledButton(
              onPressed: busy ? null : next,
              child: Text(step == 6 ? 'Submit Registration' : 'Continue'),
            ),
          ],
        ),
      ),
    );
  }
}
