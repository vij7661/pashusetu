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
  String? result;

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
                          );
                      setState(() => result = 'Pickup recorded. State ${x['transaction_state']}');
                    } catch (e) {
                      setState(() => result = e.toString());
                    }
                  },
            child: const Text('Verify Pickup & Departure'),
          ),
        ]),
      ),
    );
  }
}
