import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/language_provider.dart';
import '../providers.dart';
import 'transaction_models.dart';
import 'transaction_state_strings.dart';
import 'transaction_strings.dart';

class TransactionScreen extends ConsumerWidget {
  const TransactionScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    String t(String key) => TransactionStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('transaction'))),
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
                  subtitle: Text(
                    '${t('state')}: ${TransactionStateStrings.label(language, tx.state)}',
                  ),
                ),
              ),
              Text(t('transaction_truth_note')),
            ],
          );
        },
      ),
    );
  }
}
