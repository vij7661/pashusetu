import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../providers.dart';

class WeighmentAckScreen extends ConsumerStatefulWidget {
  const WeighmentAckScreen({super.key, required this.weighmentId});
  final String weighmentId;

  @override
  ConsumerState<WeighmentAckScreen> createState() => _WeighmentAckScreenState();
}

class _WeighmentAckScreenState extends ConsumerState<WeighmentAckScreen> {
  bool acknowledged = false;
  String? message;

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('farmer_acknowledgement'))),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              child: ListTile(
                title: Text(t('verified_weighment')),
                subtitle: Text(t('review_weighment_note')),
              ),
            ),
            CheckboxListTile(
              value: acknowledged,
              onChanged: (v) => setState(() => acknowledged = v ?? false),
              title: Text(t('i_acknowledge')),
              subtitle: Text(t('ack_confirm_note')),
            ),
            if (message != null) Text(message!),
            const Spacer(),
            OutlinedButton(
              onPressed: () async {
                try {
                  await ref.read(weighmentRepositoryProvider).reject(widget.weighmentId);
                  if (!mounted) return;
                  setState(() => message = t('reweigh_required'));
                } catch (e) {
                  if (!mounted) return;
                  setState(() => message = e.toString());
                }
              },
              child: Text(t('reject_reweigh')),
            ),
            const SizedBox(height: 8),
            FilledButton(
              onPressed: acknowledged
                  ? () async {
                      try {
                        await ref
                            .read(weighmentRepositoryProvider)
                            .acknowledge(widget.weighmentId);
                        final receipt = await ref
                            .read(weighmentRepositoryProvider)
                            .createReceipt(widget.weighmentId);
                        if (!mounted) return;
                        setState(
                          () => message =
                              '${t('i_acknowledge')} ✓ · ${receipt['receipt_code']}',
                        );
                      } catch (e) {
                        if (!mounted) return;
                        setState(() => message = e.toString());
                      }
                    }
                  : null,
              child: Text(t('set_price_listing')),
            ),
          ],
        ),
      ),
    );
  }
}
