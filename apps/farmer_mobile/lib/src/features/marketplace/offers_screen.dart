import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/money.dart';
import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../providers.dart';

class OffersScreen extends ConsumerWidget {
  const OffersScreen({super.key, required this.listingId});
  final String listingId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);
    return Scaffold(
      appBar: AppBar(title: Text(t('buyer_offers'))),
      body: FutureBuilder(
        future: ref.read(marketplaceRepositoryProvider).bids(listingId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text(snapshot.error.toString()));
          }
          final bids = snapshot.data ?? [];
          if (bids.isEmpty) return Center(child: Text(t('no_offers')));
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: bids.length,
            itemBuilder: (context, i) {
              final b = bids[i];
              return Card(
                child: ListTile(
                  title: Text('${formatPaise(b.pricePerKgPaise)}/kg'),
                  subtitle: Text(
                    '${t('total')}: ${formatPaise(b.totalOfferPaise)}\n'
                    '${t('server_sequence')} #${b.serverSequence}',
                  ),
                  trailing: FilledButton(
                    onPressed: b.status == 'ACTIVE'
                        ? () async {
                            final accepted = await ref
                                .read(marketplaceRepositoryProvider)
                                .acceptBid(listingId, b.id);
                            if (context.mounted) {
                              context.go(
                                '/transaction/${accepted['transaction_id']}/agreement',
                              );
                            }
                          }
                        : null,
                    child: Text(t('accept')),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
