import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../shared/money.dart';
import '../providers.dart';
import 'transaction_models.dart';

class SettlementScreen extends ConsumerStatefulWidget {
  const SettlementScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  ConsumerState<SettlementScreen> createState() => _SettlementScreenState();
}

class _SettlementScreenState extends ConsumerState<SettlementScreen> {
  SettlementView? result;
  String? error;
  bool loading = false;

  Future<void> loadSettlement() async {
    if (loading) return;
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final settlement = await ref
          .read(transactionRepositoryProvider)
          .settlement(widget.transactionId);
      if (!mounted) return;
      setState(() => result = settlement);
    } catch (exception) {
      if (!mounted) return;
      setState(() {
        result = null;
        error = exception.toString();
      });
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('settlement'))),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (result != null)
              Card(
                child: ListTile(
                  title: Text(t('final_settlement')),
                  subtitle: Text(
                    '${t('gross')} ${formatPaise(result!.grossAmountPaise)}\n'
                    '${t('adjustment')} ${formatPaise(result!.adjustmentPaise)}\n'
                    '${t('platform_fee')} ${formatPaise(result!.platformFeePaise)}',
                  ),
                  trailing: Text(
                    formatPaise(result!.finalAmountPaise),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            if (error != null)
              Text(error!, style: const TextStyle(color: Colors.red)),
            const Spacer(),
            FilledButton(
              onPressed: loading ? null : loadSettlement,
              child: loading
                  ? const SizedBox.square(
                      dimension: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(t('load_complete_settlement')),
            ),
          ],
        ),
      ),
    );
  }
}
