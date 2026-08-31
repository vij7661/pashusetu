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

  test('agreement contract requires backend-owned commercial terms', () {
    final agreement = AgreementView.fromJson({
      'agreement_id': 'AGR-001',
      'transaction_id': 'TX-001',
      'version': 1,
      'price_basis': 'DELIVERY_ADJUSTED_NET_KG',
      'pickup_point': 'Verified pickup point',
      'final_weighing_point': 'Verified final scale',
      'tolerance_percent': 1.5,
      'transport_responsibility': 'BUYER',
      'dispute_rule': 'Controlled reweigh',
      'farmer_confirmed': true,
      'buyer_confirmed': false,
      'locked': false,
      'status': 'PENDING_CONFIRMATION',
    });

    expect(agreement.priceBasis, 'DELIVERY_ADJUSTED_NET_KG');
    expect(agreement.transportResponsibility, 'BUYER');
    expect(agreement.farmerConfirmed, isTrue);
    expect(agreement.locked, isFalse);
  });

  test('agreement contract rejects malformed confirmation state', () {
    expect(
      () => AgreementView.fromJson({
        'agreement_id': 'AGR-001',
        'transaction_id': 'TX-001',
        'version': 1,
        'price_basis': 'DELIVERY_ADJUSTED_NET_KG',
        'pickup_point': 'Verified pickup point',
        'final_weighing_point': 'Verified final scale',
        'tolerance_percent': 1.5,
        'transport_responsibility': 'BUYER',
        'dispute_rule': 'Controlled reweigh',
        'farmer_confirmed': 'true',
        'buyer_confirmed': false,
        'locked': false,
        'status': 'PENDING_CONFIRMATION',
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
