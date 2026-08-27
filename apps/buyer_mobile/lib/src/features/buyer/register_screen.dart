import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});
  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  int step = 0;
  final mobile = TextEditingController(text: '+919876512345');
  final otp = TextEditingController(text: '4816');
  final business = TextEditingController(text: 'Hyderabad Meat Traders');
  final contact = TextEditingController(text: 'Imran');
  final city = TextEditingController(text: 'Hyderabad');
  String buyerType = 'BULK_BUYER';
  String language = 'te';
  bool busy = false;
  String? error;

  Future<void> next() async {
    setState(() { busy = true; error = null; });
    try {
      if (step == 0) {
        await ref.read(authRepositoryProvider).requestOtp(mobile.text.trim());
      } else if (step == 1) {
        await ref.read(authRepositoryProvider).verifyOtp(mobile.text.trim(), otp.text.trim());
      } else if (step == 4) {
        await ref.read(buyerRepositoryProvider).createBuyer(
          businessName: business.text.trim(),
          buyerType: buyerType,
          language: language,
          contactPerson: contact.text.trim(),
          city: city.text.trim(),
        );
      }
      if (!mounted) return;
      if (step >= 5) {
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
    Widget body;
    final titles = [
      'Mobile Verification',
      'Verify OTP',
      'Choose Language',
      'Buyer / Business Details',
      'Buyer KYC',
      'Review Registration',
    ];
    switch (step) {
      case 0:
        body = TextField(controller: mobile, decoration: const InputDecoration(labelText: 'Mobile number'));
      case 1:
        body = TextField(controller: otp, decoration: const InputDecoration(labelText: 'OTP'));
      case 2:
        body = DropdownButtonFormField<String>(
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
        body = Column(children: [
          TextField(controller: business, decoration: const InputDecoration(labelText: 'Buyer / Business name')),
          const SizedBox(height: 10),
          TextField(controller: contact, decoration: const InputDecoration(labelText: 'Contact person')),
          const SizedBox(height: 10),
          DropdownButtonFormField<String>(
            initialValue: buyerType,
            items: const [
              DropdownMenuItem(value: 'INDIVIDUAL_RETAILER', child: Text('Individual Retailer')),
              DropdownMenuItem(value: 'PROPRIETORSHIP', child: Text('Proprietorship')),
              DropdownMenuItem(value: 'COMPANY', child: Text('Company')),
              DropdownMenuItem(value: 'BULK_BUYER', child: Text('Bulk Buyer')),
              DropdownMenuItem(value: 'OTHER', child: Text('Other')),
            ],
            onChanged: (v) => setState(() => buyerType = v ?? 'BULK_BUYER'),
          ),
          const SizedBox(height: 10),
          TextField(controller: city, decoration: const InputDecoration(labelText: 'City / Market')),
        ]);
      case 4:
        body = const Text(
          'KYC screen is retained, but the exact document set depends on buyer type and the selected compliant KYC provider.',
        );
      default:
        body = const Text('Review buyer registration and submit.');
    }

    return Scaffold(
      appBar: AppBar(title: Text(titles[step])),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          LinearProgressIndicator(value: (step + 1) / titles.length),
          const SizedBox(height: 20),
          Expanded(child: SingleChildScrollView(child: body)),
          if (error != null) Text(error!, style: const TextStyle(color: Colors.red)),
          FilledButton(
            onPressed: busy ? null : next,
            child: Text(step == 5 ? 'Submit Registration' : 'Continue'),
          ),
        ]),
      ),
    );
  }
}
