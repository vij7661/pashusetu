import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/money.dart';
import '../providers.dart';

class ActiveBidScreen extends ConsumerWidget {
  const ActiveBidScreen({super.key, required this.listingId});
  final String listingId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Active Bids')),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: ref.read(marketplaceRepositoryProvider).bids(listingId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text(snapshot.error.toString()));
          }
          final rows = snapshot.data ?? [];
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: rows.length,
            itemBuilder: (_, i) {
              final x = rows[i];
              return Card(
                child: ListTile(
                  title:
                      Text('${formatPaise(x['price_per_kg_paise'] as int)}/kg'),
                  subtitle: Text(
                    'Total ${formatPaise(x['total_offer_paise'] as int)}\n'
                    'Server sequence #${x['server_sequence']}',
                  ),
                  trailing: x['transaction_id'] != null
                      ? FilledButton(
                          onPressed: () => context.go(
                            '/transaction/${x['transaction_id']}/agreement',
                          ),
                          child: const Text('Agreement'),
                        )
                      : Text(x['status'].toString()),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
