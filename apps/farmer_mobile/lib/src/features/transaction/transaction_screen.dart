import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers.dart';
import 'transaction_models.dart';

class TransactionScreen extends ConsumerWidget {
  const TransactionScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Transaction')),
      body: FutureBuilder<TransactionView>(
        future: ref.read(transactionRepositoryProvider).transaction(transactionId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) return Center(child: Text(snapshot.error.toString()));
          final tx = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: ListTile(
                  title: Text(tx.id),
                  subtitle: Text('State: ${tx.state}'),
                ),
              ),
              const Text(
                'This screen renders the authoritative backend transaction state. '
                'The app does not maintain an independent transaction status.',
              ),
            ],
          );
        },
      ),
    );
  }
}
