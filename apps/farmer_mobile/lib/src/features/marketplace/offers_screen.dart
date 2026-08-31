import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/money.dart';
import '../providers.dart';

class OffersScreen extends ConsumerWidget {
  const OffersScreen({super.key, required this.listingId});
  final String listingId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Buyer Offers')),
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
          if (bids.isEmpty) {
            return const Center(child: Text('No offers yet.'));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: bids.length,
            itemBuilder: (context, i) {
              final bid = bids[i];
              return Card(
                child: ListTile(
                  title: Text('${formatPaise(bid.pricePerKgPaise)}/kg'),
                  subtitle: Text(
                    'Total: ${formatPaise(bid.totalOfferPaise)}\n'
                    'Server sequence #${bid.serverSequence}',
                  ),
                  trailing: FilledButton(
                    onPressed: bid.status == 'ACTIVE'
                        ? () async {
                            try {
                              await ref
                                  .read(marketplaceRepositoryProvider)
                                  .acceptBid(listingId, bid.id);
                              final transaction = await ref
                                  .read(transactionRepositoryProvider)
                                  .createFromListing(listingId);
                              if (!context.mounted) return;
                              final transactionId =
                                  transaction['transaction_id'].toString();
                              context.go('/transaction/$transactionId');
                            } catch (error) {
                              if (!context.mounted) return;
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text(error.toString())),
                              );
                            }
                          }
                        : null,
                    child: const Text('Accept'),
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
