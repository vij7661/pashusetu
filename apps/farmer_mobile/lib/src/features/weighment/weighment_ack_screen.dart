import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

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
  bool busy = false;
  String? result;

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('farmer_acknowledgement'))),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(t('review_weighment_note')),
            const SizedBox(height: 16),
            CheckboxListTile(
              contentPadding: EdgeInsets.zero,
              value: acknowledged,
              onChanged: busy
                  ? null
                  : (value) => setState(() => acknowledged = value ?? false),
              title: Text(t('ack_confirm_note')),
            ),
            if (result != null) Text(result!),
            const Spacer(),
            FilledButton(
              onPressed: !acknowledged || busy
                  ? null
                  : () async {
                      setState(() {
                        busy = true;
                        result = null;
                      });
                      try {
                        final repository = ref.read(weighmentRepositoryProvider);
                        final ack = await repository.acknowledge(widget.weighmentId);
                        if (ack.status != 'ACKNOWLEDGED_BY_FARMER') {
                          throw StateError('Unexpected acknowledgement status: ${ack.status}');
                        }
                        final receipt = await repository.createReceipt(widget.weighmentId);
                        if (!context.mounted) return;
                        context.go(
                          '/listing/create?target_type=${Uri.encodeQueryComponent(receipt.targetType)}'
                          '&target_id=${Uri.encodeQueryComponent(receipt.targetId)}'
                          '&receipt_code=${Uri.encodeQueryComponent(receipt.receiptCode)}',
                        );
                      } catch (e) {
                        if (mounted) setState(() => result = e.toString());
                      } finally {
                        if (mounted) setState(() => busy = false);
                      }
                    },
              child: Text(t('set_price_listing')),
            ),
          ],
        ),
      ),
    );
  }
}
