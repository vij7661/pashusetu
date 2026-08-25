import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers.dart';

class DisputeReweighScreen extends ConsumerStatefulWidget {
  const DisputeReweighScreen({super.key});

  @override
  ConsumerState<DisputeReweighScreen> createState() => _DisputeReweighScreenState();
}

class _DisputeReweighScreenState extends ConsumerState<DisputeReweighScreen> {
  final original = TextEditingController();
  String? result;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Controlled Reweigh')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          const Card(
            child: ListTile(
              title: Text('Restricted workflow'),
              subtitle: Text(
                'Used only for farmer rejection or authorized dispute handling. '
                'Original weighment history is never overwritten.',
              ),
            ),
          ),
          TextField(
            controller: original,
            decoration: const InputDecoration(labelText: 'Original Weighment ID'),
          ),
          const SizedBox(height: 10),
          const Text(
            'Checklist: verify scale ID, tare, animal identity and witnesses. '
            'Create a new verified weighment event.',
          ),
          if (result != null) Text(result!),
          const Spacer(),
          FilledButton(
            onPressed: original.text.trim().isEmpty
                ? null
                : () async {
                    try {
                      final x = await ref.read(weighmentRepositoryProvider).reweigh(
                            weighmentId: original.text.trim(),
                            scaleCode: 'A-114',
                          );
                      setState(() => result = 'New reweigh ${x['weighment_id']} created.');
                    } catch (e) {
                      setState(() => result = e.toString());
                    }
                  },
            child: const Text('Create Reweigh Event'),
          ),
        ]),
      ),
    );
  }
}
