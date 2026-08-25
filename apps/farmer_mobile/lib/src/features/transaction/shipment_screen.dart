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
          final state = snapshot.data?['state']?.toString() ?? '-';
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(child: ListTile(title: const Text('Transaction State'), subtitle: Text(state))),
              const ListTile(leading: Icon(Icons.verified), title: Text('Origin weighment verified')),
              const ListTile(leading: Icon(Icons.qr_code), title: Text('Pickup QR verification')),
              const ListTile(leading: Icon(Icons.videocam), title: Text('Loading evidence')),
              const ListTile(leading: Icon(Icons.local_shipping), title: Text('In transit')),
              const ListTile(leading: Icon(Icons.scale), title: Text('Delivery weighment')),
              const Text(
                'This screen renders the authoritative backend transaction state. '
                'Detailed transporter/location data will be added when the provider/API is finalized.',
              ),
            ],
          );
        },
      ),
    );
  }
}
