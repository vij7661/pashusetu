import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../auth/auth_controller.dart';
import '../auth/mobile_number.dart';
import '../providers.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  int step = 0;
  final mobile = TextEditingController();
  final otp = TextEditingController();
  final name = TextEditingController();
  final village = TextEditingController();
  final mandal = TextEditingController();
  final district = TextEditingController();
  bool busy = false;
  String? error;

  Future<void> next() async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final language = ref.read(languageProvider);
      if (step == 0) {
        if (!isValidMobileNumber(mobile.text)) {
          setState(
            () => error = AppStrings.tr(language, 'invalid_mobile_number'),
          );
          return;
        }
        await ref
            .read(authControllerProvider.notifier)
            .requestOtp(mobile.text.trim());
        final authState = ref.read(authControllerProvider);
        if (authState.hasError) throw authState.error!;
      } else if (step == 1) {
        await ref
            .read(authControllerProvider.notifier)
            .verifyOtp(mobile.text.trim(), otp.text.trim());
        final authState = ref.read(authControllerProvider);
        if (authState.hasError) throw authState.error!;
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
      final msg = e.toString();
      final language = ref.read(languageProvider);
      setState(() => error = msg.contains('connection timeout')
          ? AppStrings.tr(language, 'connection_error')
          : msg);
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);
    final titles = [
      t('mobile_verification'),
      t('enter_otp'),
      t('choose_language'),
      t('farmer_details'),
      t('kyc_verification'),
      t('payout_setup'),
      t('review_registration'),
    ];

    Widget content;
    switch (step) {
      case 0:
        content = TextField(
          controller: mobile,
          decoration: InputDecoration(labelText: t('mobile_number')),
          keyboardType: TextInputType.phone,
          inputFormatters: const [MobileNumberInputFormatter()],
          autofillHints: const <String>[],
          autocorrect: false,
          enableSuggestions: false,
        );
      case 1:
        content = TextField(
          controller: otp,
          decoration: InputDecoration(labelText: t('otp')),
        );
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
          onChanged: (v) async {
            final selected = v ?? 'te';
            await ref.read(languageProvider.notifier).setLanguage(selected);
          },
        );
      case 3:
        content = Column(children: [
          TextField(
              controller: name,
              decoration: InputDecoration(labelText: t('full_name'))),
          const SizedBox(height: 10),
          TextField(
              controller: village,
              decoration: InputDecoration(labelText: t('village'))),
          const SizedBox(height: 10),
          TextField(
              controller: mandal,
              decoration: InputDecoration(labelText: t('mandal'))),
          const SizedBox(height: 10),
          TextField(
              controller: district,
              decoration: InputDecoration(labelText: t('district'))),
        ]);
      case 4:
        content = Column(children: [
          const Icon(Icons.verified_user_outlined, size: 40),
          Text(t('aadhaar_note')),
        ]);
      case 5:
        content = Column(children: [
          const Icon(Icons.account_balance_outlined, size: 40),
          Text(t('payout_note')),
        ]);
      default:
        content = Text(t('review_note'));
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
            if (error != null)
              Text(error!, style: const TextStyle(color: Colors.red)),
            FilledButton(
              onPressed: busy ? null : next,
              child: Text(step == 6 ? t('submit_registration') : t('continue')),
            ),
          ],
        ),
      ),
    );
  }
}
