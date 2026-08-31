import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers.dart';

class TransactionsScreen extends ConsumerWidget {
  const TransactionsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Transactions')),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: ref.read(transactionRepositoryProvider).myTransactions(),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text(snapshot.error.toString()));
          }
          final rows = snapshot.data ?? const [];
          if (rows.isEmpty) {
            return const Center(child: Text('No transactions yet.'));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: rows.length,
            itemBuilder: (context, index) {
              final transaction = rows[index];
              final id = transaction['transaction_id'].toString();
              return Card(
                child: ListTile(
                  title: Text(id),
                  subtitle: Text(
                    'Listing ${transaction['listing_id']}\nState: ${transaction['state']}',
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => context.go('/transaction/$id'),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
