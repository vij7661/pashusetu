import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers.dart';

class FarmerReviewScreen extends ConsumerStatefulWidget {
  const FarmerReviewScreen({super.key, required this.weighmentId});
  final String weighmentId;

  @override
  ConsumerState<FarmerReviewScreen> createState() => _FarmerReviewScreenState();
}

class _FarmerReviewScreenState extends ConsumerState<FarmerReviewScreen> {
  String? message;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Farmer Review')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          const Card(
            child: ListTile(
              title: Text('Show farmer the verified record'),
              subtitle: Text(
                'Net weight · gross/tare · Scale ID · Centre ID · Operator · video evidence',
              ),
            ),
          ),
          const Text(
            'Correct flow: Farmer Rejects → fresh reweigh. '
            'Farmer Accepts → Farmer acknowledgement. '
            'There is no acknowledgement-to-scale loop.',
          ),
          if (message != null) Text(message!),
          const Spacer(),
          Row(children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () async {
                  try {
                    final x = await ref.read(weighmentRepositoryProvider).reweigh(
                          weighmentId: widget.weighmentId,
                          scaleCode: 'A-114',
                        );
                    if (mounted) {
                      context.go(
                        '/weighment/${x['weighment_id']}/review',
                      );
                    }
                  } catch (e) {
                    setState(() => message = e.toString());
                  }
                },
                child: const Text('Farmer Rejects → Reweigh'),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: FilledButton(
                onPressed: () => context.go('/weighment/${widget.weighmentId}/handoff'),
                child: const Text('Farmer Accepts'),
              ),
            ),
          ]),
        ]),
      ),
    );
  }
}
