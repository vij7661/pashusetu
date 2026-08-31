import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/kyc_status_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../core/localization/profile_strings.dart';
import 'farmer_profile.dart';
import '../providers.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    String t(String key) => ProfileStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('title'))),
      body: FutureBuilder<FarmerProfile>(
        future: ref.read(identityRepositoryProvider).farmerMe(),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || !snapshot.hasData) {
            return Center(child: Text(t('profile_error')));
          }

          final profile = snapshot.data!;
          String optional(String? value) => value ?? t('not_available');

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const CircleAvatar(radius: 36, child: Icon(Icons.person, size: 36)),
              const SizedBox(height: 12),
              Center(child: Text(profile.fullName)),
              const SizedBox(height: 20),
              ListTile(title: Text(t('farmer_id')), subtitle: Text(profile.farmerId)),
              ListTile(title: Text(t('village')), subtitle: Text(optional(profile.village))),
              ListTile(title: Text(t('mandal')), subtitle: Text(optional(profile.mandal))),
              ListTile(title: Text(t('district')), subtitle: Text(optional(profile.district))),
              ListTile(title: Text(t('state')), subtitle: Text(optional(profile.state))),
              ListTile(
                title: Text(t('kyc_status')),
                subtitle: Text(KycStatusStrings.statusLabel(language, profile.kycStatus)),
              ),
              ListTile(title: Text(t('payout_status')), subtitle: Text(profile.payoutStatus)),
            ],
          );
        },
      ),
    );
  }
}
