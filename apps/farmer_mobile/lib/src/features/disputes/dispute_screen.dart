import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
    return Scaffold(
      appBar: AppBar(title: const Text('Open Dispute')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          DropdownButtonFormField<String>(
            initialValue: reason,
            items: const [
              DropdownMenuItem(value: 'WEIGHT_DIFFERENCE', child: Text('Weight difference')),
              DropdownMenuItem(value: 'WRONG_ANIMAL', child: Text('Wrong animal')),
              DropdownMenuItem(value: 'QUANTITY_MISMATCH', child: Text('Quantity mismatch')),
              DropdownMenuItem(value: 'OTHER', child: Text('Other')),
            ],
            onChanged: (v) => setState(() => reason = v ?? 'WEIGHT_DIFFERENCE'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: amount,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Disputed amount in paise'),
          ),
          const SizedBox(height: 12),
          const Text(
            'Only the disputed amount should be held where supported. '
            'Evidence and controlled reweighing determine resolution.',
          ),
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
                setState(() => result = 'Dispute ${x['dispute_id']} opened.');
              } catch (e) {
                setState(() => result = e.toString());
              }
            },
            child: const Text('Open Dispute'),
          ),
        ]),
      ),
    );
  }
}
