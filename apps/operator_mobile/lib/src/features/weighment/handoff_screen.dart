import 'package:flutter/material.dart';

class HandoffScreen extends StatelessWidget {
  const HandoffScreen({super.key, required this.weighmentId});
  final String weighmentId;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Farmer Acknowledgement Handoff')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          const Icon(Icons.phone_android, size: 72),
          const SizedBox(height: 16),
          const Text(
            'Farmer accepted the displayed record. '
            'The Farmer app must now acknowledge the same backend weighment ID.',
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          SelectableText(
            weighmentId,
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          const Text(
            'Operator does not acknowledge on behalf of the farmer unless the approved assisted method is explicitly used.',
          ),
        ]),
      ),
    );
  }
}
