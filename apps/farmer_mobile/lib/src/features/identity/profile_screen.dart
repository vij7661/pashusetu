import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/language_provider.dart';
import '../auth/auth_error_message.dart';
import '../providers.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('My Profile')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: ref.read(identityRepositoryProvider).farmerMe(),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text(authErrorMessage(snapshot.error!, language)),
            );
          }
          final p = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const CircleAvatar(
                  radius: 36, child: Icon(Icons.person, size: 36)),
              const SizedBox(height: 12),
              Center(child: Text(p['full_name']?.toString() ?? 'Farmer')),
              const SizedBox(height: 20),
              ListTile(
                  title: const Text('Farmer ID'),
                  subtitle: Text(p['farmer_id'].toString())),
              ListTile(
                  title: const Text('Village'),
                  subtitle: Text(p['village']?.toString() ?? '-')),
              ListTile(
                  title: const Text('Mandal'),
                  subtitle: Text(p['mandal']?.toString() ?? '-')),
              ListTile(
                  title: const Text('KYC status'),
                  subtitle: Text(p['kyc_status'].toString())),
              ListTile(
                  title: const Text('Payout status'),
                  subtitle: Text(p['payout_status'].toString())),
            ],
          );
        },
      ),
    );
  }
}
