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
  bool submitting = false;

  int? get disputedAmountPaise {
    final value = int.tryParse(amount.text.trim());
    if (value == null || value < 0) return null;
    return value;
  }

  @override
  void dispose() {
    amount.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);
    final validAmount = disputedAmountPaise;

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
              onChanged: submitting
                  ? null
                  : (v) => setState(() => reason = v ?? 'WEIGHT_DIFFERENCE'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: amount,
              enabled: !submitting,
              keyboardType: TextInputType.number,
              onChanged: (_) => setState(() {}),
              decoration: InputDecoration(labelText: t('disputed_amount')),
            ),
            const SizedBox(height: 12),
            Text(t('dispute_note')),
            const Spacer(),
            if (result != null) Text(result!),
            FilledButton(
              onPressed: submitting || validAmount == null
                  ? null
                  : () async {
                      setState(() {
                        submitting = true;
                        result = null;
                      });
                      try {
                        final dispute = await ref.read(disputeRepositoryProvider).open(
                              transactionId: widget.transactionId,
                              reason: reason,
                              disputedAmountPaise: validAmount,
                            );
                        if (!mounted) return;
                        setState(() {
                          submitting = false;
                          result = dispute.id;
                        });
                      } catch (e) {
                        if (!mounted) return;
                        setState(() {
                          submitting = false;
                          result = e.toString();
                        });
                      }
                    },
              child: submitting
                  ? const SizedBox.square(
                      dimension: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(t('open_dispute')),
            ),
          ],
        ),
      ),
    );
  }
}
