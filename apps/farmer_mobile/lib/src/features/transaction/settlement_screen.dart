import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../core/providers.dart';
import '../auth/auth_error_message.dart';
import '../../shared/money.dart';

class SettlementScreen extends ConsumerStatefulWidget {
  const SettlementScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  ConsumerState<SettlementScreen> createState() => _SettlementScreenState();
}

class _SettlementScreenState extends ConsumerState<SettlementScreen> {
  Map<String, dynamic>? result;
  String? error;

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
                    '${t('gross')} ${formatPaise(result!['gross_amount_paise'] as int)}\n'
                    '${t('adjustment')} ${formatPaise(result!['adjustment_paise'] as int)}\n'
                    '${t('platform_fee')} ${formatPaise(result!['platform_fee_paise'] as int)}',
                  ),
                  trailing: Text(
                    formatPaise(result!['final_amount_paise'] as int),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            if (error != null)
              Text(error!, style: const TextStyle(color: Colors.red)),
            const Spacer(),
            FilledButton(
              onPressed: () async {
                try {
                  final x = await ref.read(apiClientProvider).post(
                        '/payments/transactions/${widget.transactionId}/settle',
                      );
                  if (!mounted) return;
                  setState(() => result = x);
                } catch (e) {
                  if (!mounted) return;
                  setState(() => error = authErrorMessage(e, language));
                }
              },
              child: Text(t('load_complete_settlement')),
            ),
          ],
        ),
      ),
    );
  }
}
