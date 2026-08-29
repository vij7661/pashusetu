import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers.dart';

class ShipmentScreen extends ConsumerWidget {
  const ShipmentScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pickup & Delivery Tracking')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: ref.read(transactionRepositoryProvider).transaction(transactionId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) return Center(child: Text(snapshot.error.toString()));

          final state = snapshot.data?['state']?.toString();
          if (state == null || state.isEmpty) {
            return const Center(child: Text('Transaction state is unavailable.'));
          }

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: ListTile(
                  leading: const Icon(Icons.local_shipping_outlined),
                  title: const Text('Authoritative transaction state'),
                  subtitle: Text(state),
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                'Shipment milestones are shown only when the backend provides verified '
                'pickup, transit, delivery, weighment, or evidence events. This screen '
                'does not infer completed milestones from static UI steps.',
              ),
            ],
          );
        },
      ),
    );
  }
}
