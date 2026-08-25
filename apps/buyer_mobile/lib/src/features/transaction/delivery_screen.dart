import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers.dart';

class DeliveryScreen extends ConsumerStatefulWidget {
  const DeliveryScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  ConsumerState<DeliveryScreen> createState() => _DeliveryScreenState();
}

class _DeliveryScreenState extends ConsumerState<DeliveryScreen> {
  final weighment = TextEditingController();
  final count = TextEditingController(text: '8');
  Map<String,dynamic>? result;
  String? error;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Delivery Verification')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          const Card(
            child: ListTile(
              title: Text('QR verified'),
              subtitle: Text('Delivery requires QR identity verification before final weighment.'),
            ),
          ),
          TextField(
            controller: weighment,
            decoration: const InputDecoration(labelText: 'Verified delivery weighment ID'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: count,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Goat count'),
          ),
          if (result != null)
            Card(
              child: ListTile(
                title: Text(
                  result!['within_tolerance'] == true ? 'Within tolerance' : 'Outside tolerance',
                ),
                subtitle: Text(
                  'Origin ${result!['origin_weight_kg']} kg\n'
                  'Delivery ${result!['delivery_weight_kg']} kg\n'
                  'Difference ${result!['difference_percent']}%\n'
                  'Route ${result!['route']}',
                ),
              ),
            ),
          if (error != null) Text(error!, style: const TextStyle(color: Colors.red)),
          const Spacer(),
          FilledButton(
            onPressed: () async {
              try {
                final x = await ref.read(logisticsRepositoryProvider).delivery(
                  transactionId: widget.transactionId,
                  deliveryWeighmentId: weighment.text.trim(),
                  goatCount: int.parse(count.text),
                );
                setState(() => result = x);
              } catch (e) {
                setState(() => error = e.toString());
              }
            },
            child: const Text('Verify Delivery'),
          ),
        ]),
      ),
    );
  }
}
