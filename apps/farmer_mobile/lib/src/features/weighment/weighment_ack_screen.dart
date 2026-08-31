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
  bool busy = false;
  String? message;

  Future<void> _accept() async {
    setState(() {
      busy = true;
      message = null;
    });
    try {
      await ref.read(weighmentRepositoryProvider).acknowledge(
            widget.weighmentId,
            acknowledged: true,
          );
      final receipt = await ref
          .read(weighmentRepositoryProvider)
          .createReceipt(widget.weighmentId);
      if (!mounted) return;
      setState(() => message = '✓ ${receipt['receipt_code']}');
    } catch (e) {
      if (!mounted) return;
      setState(() => message = e.toString());
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> _reject() async {
    setState(() {
      busy = true;
      message = null;
    });
    try {
      final result = await ref.read(weighmentRepositoryProvider).acknowledge(
            widget.weighmentId,
            acknowledged: false,
          );
      if (!mounted) return;
      setState(
        () => message =
            '${result['status']} · Return the goat/lot to the Operator for a fresh reweigh.',
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => message = e.toString());
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
      body: FutureBuilder<Map<String, dynamic>>(
        future: ref.read(weighmentRepositoryProvider).review(widget.weighmentId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text(snapshot.error.toString()));
          }

          final review = snapshot.data!;
          final evidencePresent =
              review['verification_evidence_present'] == true;
          final status = review['status']?.toString() ?? '-';
          final canDecide = status == 'FARMER_REVIEW';

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${review['net_kg']} kg',
                        style: Theme.of(context).textTheme.headlineMedium,
                      ),
                      const SizedBox(height: 12),
                      Text('${review['target_type']} · ${review['target_id']}'),
                      Text('${review['centre_name']} · ${review['centre_code']}'),
                      Text('Scale ${review['scale_code']} · Operator ${review['operator_code']}'),
                      Text(
                        evidencePresent
                            ? 'Verification video recorded ✓'
                            : 'Verification video not recorded',
                      ),
                      const SizedBox(height: 8),
                      Text('Status: $status'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Text(t('review_weighment_note')),
              CheckboxListTile(
                value: acknowledged,
                onChanged: !canDecide || busy
                    ? null
                    : (v) => setState(() => acknowledged = v ?? false),
                title: Text(t('i_acknowledge')),
                subtitle: Text(t('ack_confirm_note')),
              ),
              if (message != null) ...[
                const SizedBox(height: 8),
                Text(message!),
              ],
              const SizedBox(height: 20),
              FilledButton(
                onPressed: canDecide && acknowledged && !busy ? _accept : null,
                child: Text(t('i_acknowledge')),
              ),
              const SizedBox(height: 10),
              OutlinedButton.icon(
                onPressed: canDecide && !busy ? _reject : null,
                icon: const Icon(Icons.replay_outlined),
                label: const Text('Reject & request reweigh'),
              ),
            ],
          );
        },
      ),
    );
  }
}
