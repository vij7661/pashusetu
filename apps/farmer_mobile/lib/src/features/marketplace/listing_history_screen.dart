import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../core/localization/marketplace_strings.dart';
import '../../shared/money.dart';
import '../providers.dart';

class ListingHistoryScreen extends ConsumerWidget {
  const ListingHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('your_listings'))),
      body: FutureBuilder(
        future: ref.read(marketplaceRepositoryProvider).myListings(),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) return Center(child: Text(snapshot.error.toString()));
          final rows = snapshot.data ?? [];
          if (rows.isEmpty) {
            return Center(child: Text(MarketplaceStrings.tr(language, 'no_listings')));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: rows.length,
            itemBuilder: (_, i) {
              final x = rows[i];
              return Card(
                child: ListTile(
                  title: Text(x.id),
                  subtitle: Text(
                    '${x.verifiedWeightKg} kg · ${formatPaise(x.pricePerKgPaise)}/kg\n'
                    '${t('total')} ${formatPaise(x.totalValuePaise)}',
                  ),
                  trailing: Text(MarketplaceStrings.listingStatus(language, x.status)),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
