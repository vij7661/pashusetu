import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/kyc_status_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../shared/app_card.dart';
import '../identity/farmer_dashboard.dart';
import '../providers.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);
    String kyc(String key) => KycStatusStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.go('/profile'),
          icon: const CircleAvatar(child: Icon(Icons.person)),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(t('namaste')),
            Text(t('farmer_dashboard'), style: const TextStyle(fontSize: 12)),
          ],
        ),
      ),
      body: FutureBuilder<FarmerDashboard>(
        future: ref.read(identityRepositoryProvider).farmerDashboard(),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || !snapshot.hasData) {
            return Center(child: Text(kyc('dashboard_state_error')));
          }

          final dashboard = snapshot.data!;
          final settledRupees =
              (dashboard.settledAmountPaise / 100).toStringAsFixed(0);

          String kycTitle() {
            switch (dashboard.kycStatus) {
              case 'KYC_ACTION_REQUIRED':
                return kyc('action_required');
              case 'KYC_REJECTED':
                return kyc('rejected');
              case 'KYC_PENDING':
                return kyc('pending');
              default:
                return kyc('incomplete');
            }
          }

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              if (!dashboard.transactionEnabled) ...[
                Card(
                  child: ListTile(
                    leading: const Icon(Icons.verified_user_outlined),
                    title: Text(kycTitle()),
                    subtitle: Text(kyc('transaction_note')),
                  ),
                ),
                const SizedBox(height: 12),
              ],
              Row(
                children: [
                  Expanded(
                    child: _Kpi(
                      value: '${dashboard.liveListings}',
                      label: t('live_listings'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _Kpi(
                      value: '${dashboard.activeOffers}',
                      label: t('offers'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _Kpi(value: '₹$settledRupees', label: t('settled')),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              AppCard(
                onTap: () => context.go('/livestock/new'),
                child: ListTile(
                  leading: const Icon(Icons.add_circle_outline),
                  title: Text(t('add_goat_lot')),
                  subtitle: Text(t('add_goat_lot_desc')),
                ),
              ),
              AppCard(
                onTap: () => context.go('/listings'),
                child: ListTile(
                  leading: const Icon(Icons.inventory_2_outlined),
                  title: Text(t('your_listings')),
                  subtitle: Text(t('your_listings_desc')),
                ),
              ),
              AppCard(
                onTap: dashboard.transactionEnabled
                    ? () => context.go('/listing/create')
                    : null,
                child: ListTile(
                  enabled: dashboard.transactionEnabled,
                  leading: const Icon(Icons.sell_outlined),
                  title: Text(t('create_verified_listing')),
                  subtitle: Text(
                    dashboard.transactionEnabled
                        ? t('create_verified_listing_desc')
                        : kyc('available_after_kyc'),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _Kpi extends StatelessWidget {
  const _Kpi({required this.value, required this.label});
  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 14),
        child: Column(children: [
          Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          Text(label, style: const TextStyle(fontSize: 9), textAlign: TextAlign.center),
        ]),
      ),
    );
  }
}
