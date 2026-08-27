import 'package:flutter/material.dart';

class DeliveryScreen extends StatelessWidget {
  const DeliveryScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Delivery Verification')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          const Card(
            child: ListTile(
              leading: Icon(Icons.verified_user),
              title: Text('Operator verification required'),
              subtitle: Text(
                'The assigned Operator records delivery evidence and the trusted final '
                'weighment. Buyer-entered weight cannot determine settlement.',
              ),
            ),
          ),
          Card(
            child: ListTile(
              title: const Text('Transaction'),
              subtitle: Text(transactionId),
            ),
          ),
        ]),
      ),
    );
  }
}
