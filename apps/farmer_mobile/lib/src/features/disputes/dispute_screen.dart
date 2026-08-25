import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../providers.dart';

class DisputeScreen extends ConsumerStatefulWidget {
  const DisputeScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  ConsumerState<DisputeScreen> createState() => _DisputeScreenState();
}

class _DisputeScreenState extends ConsumerState<DisputeScreen> {
  String reason = 'WEIGHT_DIFFERENCE';
  final amount = TextEditingController(text: '0');
  String? result;

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('open_dispute'))),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            DropdownButtonFormField<String>(
              initialValue: reason,
              items: [
                DropdownMenuItem(
                  value: 'WEIGHT_DIFFERENCE',
                  child: Text(t('weight_difference')),
                ),
                DropdownMenuItem(
                  value: 'WRONG_ANIMAL',
                  child: Text(t('wrong_animal')),
                ),
                DropdownMenuItem(
                  value: 'QUANTITY_MISMATCH',
                  child: Text(t('quantity_mismatch')),
                ),
                DropdownMenuItem(
                  value: 'OTHER',
                  child: Text(t('other')),
                ),
              ],
              onChanged: (v) =>
                  setState(() => reason = v ?? 'WEIGHT_DIFFERENCE'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: amount,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(labelText: t('disputed_amount')),
            ),
            const SizedBox(height: 12),
            Text(t('dispute_note')),
            const Spacer(),
            if (result != null) Text(result!),
            FilledButton(
              onPressed: () async {
                try {
                  final x = await ref.read(disputeRepositoryProvider).open(
                        transactionId: widget.transactionId,
                        reason: reason,
                        disputedAmountPaise: int.tryParse(amount.text) ?? 0,
                      );
                  if (!mounted) return;
                  setState(() => result = '${x['dispute_id']}');
                } catch (e) {
                  if (!mounted) return;
                  setState(() => result = e.toString());
                }
              },
              child: Text(t('open_dispute')),
            ),
          ],
        ),
      ),
    );
  }
}
