import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
          if (bids.isEmpty) return const Center(child: Text('No offers yet.'));
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: bids.length,
            itemBuilder: (context, i) {
              final b = bids[i];
              return Card(
                child: ListTile(
                  title: Text('${formatPaise(b.pricePerKgPaise)}/kg'),
                  subtitle: Text(
                    'Total: ${formatPaise(b.totalOfferPaise)}\n'
                    'Server sequence #${b.serverSequence}',
                  ),
                  trailing: FilledButton(
                    onPressed: b.status == 'ACTIVE'
                        ? () async {
                            await ref
                                .read(marketplaceRepositoryProvider)
                                .acceptBid(listingId, b.id);
                            if (context.mounted) Navigator.of(context).pop();
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
