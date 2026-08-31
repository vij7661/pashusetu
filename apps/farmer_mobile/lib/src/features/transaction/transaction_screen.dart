import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers.dart';

class TransactionScreen extends ConsumerWidget {
  const TransactionScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Transaction')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: ref.read(transactionRepositoryProvider).transaction(transactionId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text(snapshot.error.toString()));
          }
          final tx = snapshot.data!;
          final state = tx['state']?.toString() ?? '-';

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: ListTile(
                  title: Text(tx['transaction_id'].toString()),
                  subtitle: Text(
                    'Listing ${tx['listing_id']}\nState: $state',
                  ),
                ),
              ),
              const Text(
                'This state comes from the authoritative backend. The Farmer app does not maintain an independent transaction status.',
              ),
              const SizedBox(height: 16),
              if ({'OFFER_ACCEPTED', 'AGREEMENT_PENDING'}.contains(state))
                FilledButton.icon(
                  onPressed: () => context.go(
                    '/transaction/$transactionId/agreement',
                  ),
                  icon: const Icon(Icons.handshake_outlined),
                  label: const Text('Agreement'),
                ),
              if ({
                'AGREEMENT_LOCKED',
                'FUNDS_SECURED',
                'PICKUP_SCHEDULED',
                'PICKED_UP',
                'IN_TRANSIT',
                'DELIVERED',
                'DELIVERY_VERIFICATION',
                'TOLERANCE_CHECK',
              }.contains(state))
                FilledButton.icon(
                  onPressed: () => context.go(
                    '/transaction/$transactionId/shipment',
                  ),
                  icon: const Icon(Icons.local_shipping_outlined),
                  label: const Text('Pickup & Delivery'),
                ),
              if (state == 'DISPUTED')
                FilledButton.icon(
                  onPressed: () => context.go(
                    '/transaction/$transactionId/dispute',
                  ),
                  icon: const Icon(Icons.report_problem_outlined),
                  label: const Text('Dispute'),
                ),
              if ({'RESOLVED', 'SETTLED'}.contains(state))
                FilledButton.icon(
                  onPressed: () => context.go(
                    '/transaction/$transactionId/settlement',
                  ),
                  icon: const Icon(Icons.payments_outlined),
                  label: const Text('Settlement'),
                ),
              if (state == 'CLOSED')
                const Card(
                  child: ListTile(
                    leading: Icon(Icons.check_circle_outline),
                    title: Text('Transaction closed'),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}
