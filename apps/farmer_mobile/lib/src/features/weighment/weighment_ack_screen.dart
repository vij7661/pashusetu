import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../providers.dart';
import 'weighment_strings.dart';

class WeighmentAckScreen extends ConsumerStatefulWidget {
  const WeighmentAckScreen({super.key, required this.weighmentId});

  final String weighmentId;

  @override
  ConsumerState<WeighmentAckScreen> createState() => _WeighmentAckScreenState();
}

class _WeighmentAckScreenState extends ConsumerState<WeighmentAckScreen> {
  bool acknowledged = false;
  bool busy = false;
  bool rejected = false;
  String? result;

  Future<void> rejectWeighment(String language) async {
    if (busy) return;
    setState(() {
      busy = true;
      result = null;
    });
    try {
      final decision = await ref
          .read(weighmentRepositoryProvider)
          .decide(widget.weighmentId, acknowledged: false);
      if (!decision.rejected) {
        throw StateError('Unexpected weighment decision status: ${decision.status}');
      }
      if (!mounted) return;
      setState(() {
        rejected = true;
        acknowledged = false;
        result = WeighmentStrings.tr(language, 'reweigh_required');
      });
    } catch (e) {
      if (mounted) setState(() => result = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> acceptWeighment(BuildContext context) async {
    if (busy || rejected || !acknowledged) return;
    setState(() {
      busy = true;
      result = null;
    });
    try {
      final repository = ref.read(weighmentRepositoryProvider);
      final decision = await repository.decide(
        widget.weighmentId,
        acknowledged: true,
      );
      if (!decision.accepted) {
        throw StateError('Unexpected weighment decision status: ${decision.status}');
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
  }

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
              onChanged: busy || rejected
                  ? null
                  : (value) => setState(() => acknowledged = value ?? false),
              title: Text(t('ack_confirm_note')),
            ),
            if (result != null) Text(result!),
            const Spacer(),
            OutlinedButton(
              onPressed: busy || rejected ? null : () => rejectWeighment(language),
              child: Text(WeighmentStrings.tr(language, 'reject_weight')),
            ),
            const SizedBox(height: 8),
            FilledButton(
              onPressed: !acknowledged || busy || rejected
                  ? null
                  : () => acceptWeighment(context),
              child: Text(t('set_price_listing')),
            ),
          ],
        ),
      ),
    );
  }
}
