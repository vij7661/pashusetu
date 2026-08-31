import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/money.dart';
import '../providers.dart';

class ListingHistoryScreen extends ConsumerWidget {
  const ListingHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Your Listings')),
      body: FutureBuilder(
        future: ref.read(marketplaceRepositoryProvider).myListings(),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text(snapshot.error.toString()));
          }
          final rows = snapshot.data ?? [];
          if (rows.isEmpty) {
            return const Center(child: Text('No listings yet.'));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: rows.length,
            itemBuilder: (context, i) {
              final listing = rows[i];
              final canOpenOffers = {
                'PUBLISHED',
                'OFFER_ACCEPTED',
              }.contains(listing.status);
              return Card(
                child: ListTile(
                  title: Text(listing.id),
                  subtitle: Text(
                    '${listing.verifiedWeightKg} kg · '
                    '${formatPaise(listing.pricePerKgPaise)}/kg\n'
                    'Total ${formatPaise(listing.totalValuePaise)} · '
                    '${listing.status}',
                  ),
                  trailing: canOpenOffers
                      ? const Icon(Icons.chevron_right)
                      : null,
                  onTap: canOpenOffers
                      ? () => context.go('/listing/${listing.id}/offers')
                      : null,
                ),
              );
            },
          );
        },
      ),
    );
  }
}
