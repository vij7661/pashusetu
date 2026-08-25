import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers.dart';

class AgreementScreen extends ConsumerStatefulWidget {
  const AgreementScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  ConsumerState<AgreementScreen> createState() => _AgreementScreenState();
}

class _AgreementScreenState extends ConsumerState<AgreementScreen> {
  final pickup = TextEditingController(text: 'Chityal Mandal Centre');
  final finalScale = TextEditingController(text: 'Buyer Verified Scale HYD-17');
  final tolerance = TextEditingController(text: '1.5');
  String? agreementId;
  bool confirmed = false;
  String? message;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Transaction Agreement')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(controller: pickup, decoration: const InputDecoration(labelText: 'Pickup point')),
          const SizedBox(height: 10),
          TextField(controller: finalScale, decoration: const InputDecoration(labelText: 'Final weighing point')),
          const SizedBox(height: 10),
          TextField(controller: tolerance, decoration: const InputDecoration(labelText: 'Allowed tolerance %')),
          const SizedBox(height: 12),
          const Card(
            child: ListTile(
              title: Text('Transport responsibility'),
              subtitle: Text('Buyer'),
            ),
          ),
          const Card(
            child: ListTile(
              title: Text('Dispute rule'),
              subtitle: Text('Controlled reweigh → independent verified scale → evidence review'),
            ),
          ),
          if (message != null) Text(message!),
          FilledButton(
            onPressed: agreementId == null
                ? () async {
                    try {
                      final result = await ref.read(transactionRepositoryProvider).createAgreement(
                        transactionId: widget.transactionId,
                        pickupPoint: pickup.text.trim(),
                        finalWeighingPoint: finalScale.text.trim(),
                        tolerancePercent: double.parse(tolerance.text),
                      );
                      setState(() => agreementId = result['agreement_id'] as String);
                    } catch (e) {
                      setState(() => message = e.toString());
                    }
                  }
                : () async {
                    try {
                      await ref.read(transactionRepositoryProvider).confirmAgreement(
                        widget.transactionId,
                        agreementId!,
                      );
                      setState(() {
                        confirmed = true;
                        message = 'Farmer confirmed agreement. Waiting for buyer confirmation if not yet complete.';
                      });
                    } catch (e) {
                      setState(() => message = e.toString());
                    }
                  },
            child: Text(agreementId == null ? 'Create Agreement' : 'Confirm Agreement'),
          ),
          if (confirmed) const Text('✓ Farmer confirmation recorded'),
        ],
      ),
    );
  }
}
