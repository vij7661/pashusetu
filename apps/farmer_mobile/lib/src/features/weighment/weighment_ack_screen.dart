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
  bool submitting = false;
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
              onChanged: submitting
                  ? null
                  : (value) => setState(() => acknowledged = value ?? false),
              title: Text(t('i_acknowledge')),
              subtitle: Text(t('ack_confirm_note')),
            ),
            if (message != null) Text(message!),
            const Spacer(),
            FilledButton(
              onPressed: acknowledged && !submitting
                  ? () async {
                      setState(() {
                        submitting = true;
                        message = null;
                      });
                      try {
                        final repository = ref.read(weighmentRepositoryProvider);
                        await repository.acknowledge(widget.weighmentId);
                        final receipt = await repository.createReceipt(widget.weighmentId);
                        if (!mounted) return;
                        final uri = Uri(
                          path: '/listing/create',
                          queryParameters: {
                            'target_type': receipt.targetType,
                            'target_id': receipt.targetId,
                            'receipt_code': receipt.receiptCode,
                          },
                        );
                        this.context.go(uri.toString());
                      } catch (error) {
                        if (!mounted) return;
                        setState(() {
                          submitting = false;
                          message = error.toString();
                        });
                      }
                    }
                  : null,
              child: submitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(t('set_price_listing')),
            ),
          ],
        ),
      ),
    );
  }
}
