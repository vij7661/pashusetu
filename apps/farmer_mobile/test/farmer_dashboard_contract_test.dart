import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/identity/farmer_dashboard.dart';

void main() {
  test('parses a complete Farmer dashboard response', () {
    final dashboard = FarmerDashboard.fromJson({
      'farmer_id': 'PS-FRM-TEST',
      'kyc_status': 'KYC_VERIFIED',
      'transaction_enabled': true,
      'live_listings': 2,
      'active_offers': 3,
      'settled_amount_paise': 125000,
    });

    expect(dashboard.farmerId, 'PS-FRM-TEST');
    expect(dashboard.transactionEnabled, isTrue);
    expect(dashboard.liveListings, 2);
    expect(dashboard.activeOffers, 3);
    expect(dashboard.settledAmountPaise, 125000);
  });

  test('rejects incomplete dashboard data instead of inventing defaults', () {
    expect(
      () => FarmerDashboard.fromJson({
        'farmer_id': 'PS-FRM-TEST',
        'kyc_status': 'KYC_PENDING',
        'transaction_enabled': false,
        'live_listings': 0,
        'settled_amount_paise': 0,
      }),
      throwsFormatException,
    );
  });
}
