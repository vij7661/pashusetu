import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/language_provider.dart';
import '../providers.dart';
import 'transaction_strings.dart';

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
    final language = ref.watch(languageProvider);
    String t(String key) => TransactionStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('agreement_title'))),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: pickup,
            onChanged: (_) => setState(() {}),
            decoration: InputDecoration(labelText: t('pickup_point')),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: finalScale,
            onChanged: (_) => setState(() {}),
            decoration: InputDecoration(labelText: t('final_weighing_point')),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: tolerance,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (_) => setState(() {}),
            decoration: InputDecoration(labelText: t('allowed_tolerance')),
          ),
          const SizedBox(height: 12),
          if (agreementId != null) ...[
            Card(
              child: ListTile(
                title: Text(t('price_basis')),
                subtitle: Text(priceBasis ?? '—'),
              ),
            ),
            Card(
              child: ListTile(
                title: Text(t('transport_responsibility')),
                subtitle: Text(transportResponsibility ?? '—'),
              ),
            ),
            Card(
              child: ListTile(
                title: Text(t('dispute_rule')),
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
                            priceBasis = result.priceBasis;
                            transportResponsibility = result.transportResponsibility;
                            disputeRule = result.disputeRule;
                            message = confirmed ? t('farmer_confirmed_waiting') : null;
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
                : Text(agreementId == null ? t('create_agreement') : t('confirm_agreement')),
          ),
          if (confirmed) Text('✓ ${t('farmer_confirmation_recorded')}'),
        ],
      ),
    );
  }
}
