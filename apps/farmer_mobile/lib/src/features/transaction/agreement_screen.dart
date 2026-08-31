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
  final pickup = TextEditingController();
  final finalScale = TextEditingController();
  final tolerance = TextEditingController();
  String? agreementId;
  String? transportResponsibility;
  String? disputeRule;
  String? priceBasis;
  bool confirmed = false;
  bool submitting = false;
  String? message;

  bool get canCreate {
    final toleranceValue = double.tryParse(tolerance.text);
    return !submitting &&
        pickup.text.trim().length >= 3 &&
        finalScale.text.trim().length >= 3 &&
        toleranceValue != null &&
        toleranceValue > 0 &&
        toleranceValue <= 10;
  }

  @override
  void dispose() {
    pickup.dispose();
    finalScale.dispose();
    tolerance.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Transaction Agreement')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: pickup,
            onChanged: (_) => setState(() {}),
            decoration: const InputDecoration(labelText: 'Pickup point'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: finalScale,
            onChanged: (_) => setState(() {}),
            decoration: const InputDecoration(labelText: 'Final weighing point'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: tolerance,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (_) => setState(() {}),
            decoration: const InputDecoration(labelText: 'Allowed tolerance %'),
          ),
          const SizedBox(height: 12),
          if (agreementId != null) ...[
            Card(
              child: ListTile(
                title: const Text('Price basis'),
                subtitle: Text(priceBasis ?? '—'),
              ),
            ),
            Card(
              child: ListTile(
                title: const Text('Transport responsibility'),
                subtitle: Text(transportResponsibility ?? '—'),
              ),
            ),
            Card(
              child: ListTile(
                title: const Text('Dispute rule'),
                subtitle: Text(disputeRule ?? '—'),
              ),
            ),
          ],
          if (message != null) Text(message!),
          FilledButton(
            onPressed: agreementId == null
                ? (canCreate
                    ? () async {
                        setState(() {
                          submitting = true;
                          message = null;
                        });
                        try {
                          final result = await ref
                              .read(transactionRepositoryProvider)
                              .createAgreement(
                                transactionId: widget.transactionId,
                                pickupPoint: pickup.text.trim(),
                                finalWeighingPoint: finalScale.text.trim(),
                                tolerancePercent: double.parse(tolerance.text),
                              );
                          if (!mounted) return;
                          setState(() {
                            agreementId = result.id;
                            priceBasis = result.priceBasis;
                            transportResponsibility = result.transportResponsibility;
                            disputeRule = result.disputeRule;
                            submitting = false;
                          });
                        } catch (error) {
                          if (!mounted) return;
                          setState(() {
                            submitting = false;
                            message = error.toString();
                          });
                        }
                      }
                    : null)
                : (!submitting && !confirmed
                    ? () async {
                        setState(() {
                          submitting = true;
                          message = null;
                        });
                        try {
                          final result = await ref
                              .read(transactionRepositoryProvider)
                              .confirmAgreement(widget.transactionId, agreementId!);
                          if (!mounted) return;
                          setState(() {
                            submitting = false;
                            confirmed = result.farmerConfirmed;
                            message = result.locked
                                ? 'Agreement confirmed by both parties and locked.'
                                : 'Farmer confirmed agreement. Waiting for buyer confirmation.';
                          });
                        } catch (error) {
                          if (!mounted) return;
                          setState(() {
                            submitting = false;
                            message = error.toString();
                          });
                        }
                      }
                    : null),
            child: submitting
                ? const SizedBox.square(
                    dimension: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(agreementId == null ? 'Create Agreement' : 'Confirm Agreement'),
          ),
          if (confirmed) const Text('✓ Farmer confirmation recorded'),
        ],
      ),
    );
  }
}
