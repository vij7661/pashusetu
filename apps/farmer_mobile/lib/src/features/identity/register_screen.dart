import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../auth/auth_controller.dart';
import '../providers.dart';

const farmerOtpLength = 4;
const aadhaarLength = 12;

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
  final aadhaar = TextEditingController();
  String language = 'te';
  bool busy = false;
  String? error;

  String t(String key) => AppStrings.tr(language, key);

  @override
  void dispose() {
    mobile.dispose();
    otp.dispose();
    name.dispose();
    village.dispose();
    mandal.dispose();
    district.dispose();
    aadhaar.dispose();
    super.dispose();
  }

  Future<void> _restoreRegistration() async {
    final status = await ref.read(identityRepositoryProvider).registrationStatus();
    name.text = status['full_name']?.toString() ?? '';
    village.text = status['village']?.toString() ?? '';
    mandal.text = status['mandal']?.toString() ?? '';
    district.text = status['district']?.toString() ?? '';
    language = status['preferred_language']?.toString() ?? language;
    await ref.read(languageProvider.notifier).setLanguage(language);
    if (!mounted) return;
    if (status['next_step'] == 'KYC') {
      setState(() => step = 4);
    }
  }

  Future<void> next() async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      if (step == 0) {
        await ref.read(languageProvider.notifier).setLanguage(language);
        if (mounted) setState(() => step = 1);
      } else if (step == 1) {
        await ref
            .read(authControllerProvider.notifier)
            .requestRegistrationOtp(mobile.text.trim());
        if (!ref.read(authControllerProvider).hasError && mounted) {
          setState(() => step = 2);
        }
      } else if (step == 2) {
        if (otp.text.trim().length != farmerOtpLength) {
          throw Exception('OTP must be exactly $farmerOtpLength digits.');
        }
        final result = await ref
            .read(authControllerProvider.notifier)
            .verifyRegistrationOtp(mobile.text.trim(), otp.text.trim());
        if (ref.read(authControllerProvider).hasError) {
          throw ref.read(authControllerProvider).error!;
        }
        if (result?['next_step'] == 'KYC') {
          await _restoreRegistration();
        } else if (mounted) {
          setState(() => step = 3);
        }
      } else if (step == 3) {
        await ref.read(identityRepositoryProvider).saveRegistrationDetails(
              fullName: name.text.trim(),
              language: language,
              village: village.text.trim(),
              mandal: mandal.text.trim(),
              district: district.text.trim(),
            );
        if (mounted) setState(() => step = 4);
      } else if (step == 4) {
        if (aadhaar.text.trim().length != aadhaarLength) {
          throw Exception('Aadhaar number must be exactly $aadhaarLength digits.');
        }
        await ref.read(identityRepositoryProvider).submitKyc(
              aadhaarNumber: aadhaar.text.trim(),
            );
        if (!mounted) return;
        context.go('/home');
      }
    } catch (e) {
      final msg = e.toString();
      if (mounted) {
        setState(() => error = msg.contains('connection timeout')
            ? t('connection_error')
            : msg);
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final titles = [
      t('choose_language'),
      t('mobile_verification'),
      t('enter_otp'),
      t('farmer_details'),
      t('kyc_verification'),
    ];

    Widget content;
    switch (step) {
      case 0:
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
            setState(() => language = selected);
            await ref.read(languageProvider.notifier).setLanguage(selected);
          },
        );
        break;
      case 1:
        content = TextField(
          controller: mobile,
          keyboardType: TextInputType.phone,
          decoration: InputDecoration(
            labelText: t('mobile_number'),
            hintText: '+91XXXXXXXXXX',
          ),
        );
        break;
      case 2:
        content = TextField(
          controller: otp,
          keyboardType: TextInputType.number,
          maxLength: farmerOtpLength,
          inputFormatters: const [
            FilteringTextInputFormatter.digitsOnly,
            LengthLimitingTextInputFormatter(farmerOtpLength),
          ],
          decoration: InputDecoration(labelText: t('otp')),
        );
        break;
      case 3:
        content = Column(
          children: [
            TextField(
              controller: name,
              decoration: InputDecoration(labelText: t('full_name')),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: village,
              decoration: InputDecoration(labelText: t('village')),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: mandal,
              decoration: InputDecoration(labelText: t('mandal')),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: district,
              decoration: InputDecoration(labelText: t('district')),
            ),
          ],
        );
        break;
      case 4:
        content = Column(
          children: [
            TextField(
              controller: aadhaar,
              keyboardType: TextInputType.number,
              maxLength: aadhaarLength,
              inputFormatters: const [
                FilteringTextInputFormatter.digitsOnly,
                LengthLimitingTextInputFormatter(aadhaarLength),
              ],
              decoration: InputDecoration(labelText: t('aadhaar_number')),
            ),
            const SizedBox(height: 10),
            Text(t('aadhaar_note')),
          ],
        );
        break;
      default:
        content = const SizedBox.shrink();
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
              child: Text(step == 4 ? t('submit_registration') : t('continue')),
            ),
          ],
        ),
      ),
    );
  }
}
