import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/transaction/transaction_models.dart';

void main() {
  test('transaction contract requires authoritative fields', () {
    final transaction = TransactionView.fromJson({
      'transaction_id': 'TX-001',
      'listing_id': 'LST-001',
      'accepted_bid_id': 'BID-001',
      'state': 'AGREEMENT_PENDING',
      'active_agreement_id': null,
    });

    expect(transaction.id, 'TX-001');
    expect(transaction.state, 'AGREEMENT_PENDING');
    expect(transaction.activeAgreementId, isNull);
  });

  test('transaction contract rejects missing state instead of inventing one', () {
    expect(
      () => TransactionView.fromJson({
        'transaction_id': 'TX-001',
        'listing_id': 'LST-001',
        'accepted_bid_id': 'BID-001',
        'active_agreement_id': null,
      }),
      throwsFormatException,
    );
  });

  test('settlement contract requires all monetary fields', () {
    final settlement = SettlementView.fromJson({
      'settlement_id': 'STL-001',
      'gross_amount_paise': 100000,
      'adjustment_paise': -5000,
      'platform_fee_paise': 1425,
      'final_amount_paise': 93575,
      'status': 'COMPLETED',
    });

    expect(settlement.finalAmountPaise, 93575);
    expect(settlement.status, 'COMPLETED');
  });

  test('settlement contract rejects malformed money values', () {
    expect(
      () => SettlementView.fromJson({
        'settlement_id': 'STL-001',
        'gross_amount_paise': '100000',
        'adjustment_paise': 0,
        'platform_fee_paise': 1500,
        'final_amount_paise': 98500,
        'status': 'COMPLETED',
      }),
      throwsFormatException,
    );
  });
}
