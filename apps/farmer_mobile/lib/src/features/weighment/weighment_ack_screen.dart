import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
    return Scaffold(
      appBar: AppBar(title: const Text('Farmer Acknowledgement')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Card(
              child: ListTile(
                title: Text('Verified weighment'),
                subtitle: Text(
                  'Review the operator-created verified weight, Scale ID, centre and evidence before acknowledging.',
                ),
              ),
            ),
            CheckboxListTile(
              value: acknowledged,
              onChanged: (v) => setState(() => acknowledged = v ?? false),
              title: const Text('I acknowledge'),
              subtitle: const Text('I confirm the verified weighment shown to me.'),
            ),
            if (message != null) Text(message!),
            const Spacer(),
            FilledButton(
              onPressed: acknowledged
                  ? () async {
                      try {
                        await ref.read(weighmentRepositoryProvider).acknowledge(widget.weighmentId);
                        final receipt = await ref.read(weighmentRepositoryProvider).createReceipt(widget.weighmentId);
                        setState(() => message = 'Acknowledged. Receipt ${receipt['receipt_code']} created.');
                      } catch (e) {
                        setState(() => message = e.toString());
                      }
                    }
                  : null,
              child: const Text('Set Price & Listing Rules'),
            ),
          ],
        ),
      ),
    );
  }
}
