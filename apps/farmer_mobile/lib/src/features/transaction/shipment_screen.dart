import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/language_provider.dart';
import '../providers.dart';
import 'transaction_models.dart';
import 'transaction_strings.dart';

class ShipmentScreen extends ConsumerWidget {
  const ShipmentScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    String t(String key) => TransactionStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('shipment_title'))),
      body: FutureBuilder<TransactionView>(
        future: ref.read(transactionRepositoryProvider).transaction(transactionId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) return Center(child: Text(snapshot.error.toString()));

          final transaction = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: ListTile(
                  leading: const Icon(Icons.local_shipping_outlined),
                  title: Text(t('authoritative_state')),
                  subtitle: Text(transaction.state),
                ),
              ),
              const SizedBox(height: 12),
              Text(t('shipment_truth_note')),
            ],
          );
        },
      ),
    );
  }
}
