import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../shared/app_card.dart';
import '../providers.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  Future<_HomeData> _load(WidgetRef ref) async {
    final profileFuture = ref.read(identityRepositoryProvider).farmerMe();
    final listingsFuture = ref.read(marketplaceRepositoryProvider).myListings();
    final transactionsFuture =
        ref.read(transactionRepositoryProvider).myTransactions();

    final profile = await profileFuture;
    final listings = await listingsFuture;
    final transactions = await transactionsFuture;
    final published = listings.where((listing) => listing.status == 'PUBLISHED').toList();

    final bidGroups = await Future.wait(
      published.map(
        (listing) => ref.read(marketplaceRepositoryProvider).bids(listing.id),
      ),
    );
    final activeOffers = bidGroups
        .expand((offers) => offers)
        .where((offer) => offer.status == 'ACTIVE')
        .length;
    final settledTransactions = transactions
        .where(
          (transaction) => {'SETTLED', 'CLOSED'}.contains(
            transaction['state']?.toString(),
          ),
        )
        .length;

    return _HomeData(
      profile: profile,
      liveListings: published.length,
      activeOffers: activeOffers,
      settledTransactions: settledTransactions,
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);

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
      body: FutureBuilder<_HomeData>(
        future: _load(ref),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text(snapshot.error.toString()));
          }

          final data = snapshot.data!;
          final kycStatus =
              data.profile['kyc_status']?.toString() ?? 'KYC_PENDING';
          final kycVerified = kycStatus == 'KYC_VERIFIED';

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              if (!kycVerified) ...[
                const Card(
                  child: ListTile(
                    leading: Icon(Icons.verified_user_outlined),
                    title: Text('KYC verification pending'),
                    subtitle: Text(
                      'You can use Home and manage livestock while verification is pending. '
                      'Creating a market listing is enabled after KYC is verified.',
                    ),
                  ),
                ),
                const SizedBox(height: 12),
              ],
              Row(
                children: [
                  Expanded(
                    child: _Kpi(
                      value: '${data.liveListings}',
                      label: t('live_listings'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _Kpi(
                      value: '${data.activeOffers}',
                      label: t('offers'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _Kpi(
                      value: '${data.settledTransactions}',
                      label: t('settled'),
                    ),
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
                onTap: () => context.go('/transactions'),
                child: const ListTile(
                  leading: Icon(Icons.receipt_long_outlined),
                  title: Text('Transactions'),
                  subtitle: Text(
                    'Track accepted offers, agreements, delivery and settlement.',
                  ),
                ),
              ),
              AppCard(
                onTap: kycVerified ? () => context.go('/listing/create') : null,
                child: ListTile(
                  enabled: kycVerified,
                  leading: const Icon(Icons.sell_outlined),
                  title: Text(t('create_verified_listing')),
                  subtitle: Text(
                    kycVerified
                        ? t('create_verified_listing_desc')
                        : 'Available after KYC verification',
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

class _HomeData {
  const _HomeData({
    required this.profile,
    required this.liveListings,
    required this.activeOffers,
    required this.settledTransactions,
  });

  final Map<String, dynamic> profile;
  final int liveListings;
  final int activeOffers;
  final int settledTransactions;
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
        child: Column(
          children: [
            Text(
              value,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              label,
              style: const TextStyle(fontSize: 9),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
