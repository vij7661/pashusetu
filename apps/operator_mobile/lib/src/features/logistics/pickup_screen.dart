import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers.dart';

class PickupScreen extends ConsumerStatefulWidget {
  const PickupScreen({super.key});

  @override
  ConsumerState<PickupScreen> createState() => _PickupScreenState();
}

class _PickupScreenState extends ConsumerState<PickupScreen> {
  final tx = TextEditingController();
  final count = TextEditingController(text: '8');
  final weighment = TextEditingController();
  String? result;

  String _commandId(String stage) {
    final hex = DateTime.now().microsecondsSinceEpoch.toRadixString(16).padLeft(32, '0');
    final uuid = '${hex.substring(0, 8)}-${hex.substring(8, 12)}-'
        '${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
    return stage == 'evidence' ? uuid : '$stage-$uuid';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pickup Verification')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          TextField(
            controller: tx,
            decoration: const InputDecoration(labelText: 'Transaction ID / Scan QR'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: count,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Goat count'),
          ),
          const Card(
            child: ListTile(
              title: Text('Pickup evidence'),
              subtitle: Text('QR match · goat count · loading video · vehicle/driver · departure'),
            ),
          ),
          TextField(
            controller: weighment,
            decoration: const InputDecoration(
              labelText: 'Verified final weighment ID (delivery only)',
            ),
          ),
          if (result != null) Text(result!),
          const Spacer(),
          FilledButton(
            onPressed: tx.text.trim().isEmpty
                ? null
                : () async {
                    try {
                      final x = await ref.read(logisticsRepositoryProvider).pickup(
                            transactionId: tx.text.trim(),
                            goatCount: int.parse(count.text),
                            loadingVideoEvidenceId: _commandId('evidence'),
                            idempotencyKey: _commandId('pickup'),
                          );
                      setState(() => result = 'Pickup recorded. State ${x['transaction_state']}');
                    } catch (e) {
                      setState(() => result = e.toString());
                    }
                  },
            child: const Text('Verify Pickup & Departure'),
          ),
          const SizedBox(height: 8),
          FilledButton.tonal(
            onPressed: tx.text.trim().isEmpty || weighment.text.trim().isEmpty
                ? null
                : () async {
                    try {
                      final x = await ref.read(logisticsRepositoryProvider).delivery(
                            transactionId: tx.text.trim(),
                            deliveryWeighmentId: weighment.text.trim(),
                            goatCount: int.parse(count.text),
                            deliveryVideoEvidenceId: _commandId('evidence'),
                            idempotencyKey: _commandId('delivery'),
                          );
                      setState(() => result =
                          'Delivery ${x['delivery_weight_kg']} kg; route ${x['route']}');
                    } catch (e) {
                      setState(() => result = e.toString());
                    }
                  },
            child: const Text('Verify Delivery & Final Weight'),
          ),
        ]),
      ),
    );
  }
}
