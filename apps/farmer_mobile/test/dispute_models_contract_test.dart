import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/disputes/dispute_models.dart';

void main() {
  test('dispute contract requires authoritative backend fields', () {
    final dispute = DisputeView.fromJson({
      'dispute_id': 'DSP-001',
      'transaction_id': 'TX-001',
      'reason': 'WEIGHT_DIFFERENCE',
      'disputed_amount_paise': 12500,
      'status': 'OPEN',
      'settlement_adjustment_paise': 0,
      'final_decision': null,
    });

    expect(dispute.id, 'DSP-001');
    expect(dispute.disputedAmountPaise, 12500);
    expect(dispute.status, 'OPEN');
    expect(dispute.finalDecision, isNull);
  });

  test('dispute contract rejects malformed monetary fields', () {
    expect(
      () => DisputeView.fromJson({
        'dispute_id': 'DSP-001',
        'transaction_id': 'TX-001',
        'reason': 'WEIGHT_DIFFERENCE',
        'disputed_amount_paise': '12500',
        'status': 'OPEN',
        'settlement_adjustment_paise': 0,
        'final_decision': null,
      }),
      throwsFormatException,
    );
  });

  test('evidence response contract is typed and strict', () {
    final evidence = DisputeEvidenceView.fromJson({
      'evidence_id': 'EVD-001',
      'status': 'RECORDED',
    });

    expect(evidence.id, 'EVD-001');
    expect(evidence.status, 'RECORDED');
    expect(
      () => DisputeEvidenceView.fromJson({
        'evidence_id': 1,
        'status': 'RECORDED',
      }),
      throwsFormatException,
    );
  });

  test('reweigh response contract is typed and strict', () {
    final reweigh = DisputeReweighView.fromJson({
      'reweigh_id': 'RW-001',
      'stage': 'CONTROLLED',
      'status': 'RECORDED',
    });

    expect(reweigh.id, 'RW-001');
    expect(reweigh.stage, 'CONTROLLED');
    expect(reweigh.status, 'RECORDED');
    expect(
      () => DisputeReweighView.fromJson({
        'reweigh_id': 'RW-001',
        'stage': null,
        'status': 'RECORDED',
      }),
      throwsFormatException,
    );
  });
}
