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
  final amount = TextEditingController(text: '0');
  String reason = 'WEIGHT_DIFFERENCE';
  String? message;

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
          TextField(controller: amount, decoration: const InputDecoration(labelText: 'Disputed amount (paise)')),
          if (message != null) Text(message!),
          const Spacer(),
          FilledButton(
            onPressed: () async {
              try {
                final x = await ref.read(disputeRepositoryProvider).open(
                  transactionId: widget.transactionId,
                  reason: reason,
                  disputedAmountPaise: int.tryParse(amount.text) ?? 0,
                );
                setState(() => message = 'Dispute ${x['dispute_id']} opened.');
              } catch (e) {
                setState(() => message = e.toString());
              }
            },
            child: const Text('Open Dispute'),
          ),
        ]),
      ),
    );
  }
}
