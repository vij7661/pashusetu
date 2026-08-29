import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/language_provider.dart';
import '../auth/auth_error_message.dart';
import '../providers.dart';

class TransactionScreen extends ConsumerWidget {
  const TransactionScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Transaction')),
      body: FutureBuilder<Map<String, dynamic>>(
        future:
            ref.read(transactionRepositoryProvider).transaction(transactionId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text(authErrorMessage(snapshot.error!, language)),
            );
          }
          final tx = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: ListTile(
                  title: Text(tx['transaction_id'].toString()),
                  subtitle: Text('State: ${tx['state']}'),
                ),
              ),
              const Text(
                'Farmer and Buyer apps render this authoritative backend transaction state. '
                'They do not maintain independent transaction status.',
              ),
            ],
          );
        },
      ),
    );
  }
}
