import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/identity/farmer_dashboard.dart';

void main() {
  Map<String, dynamic> dashboard({
    required String kycStatus,
    required bool transactionEnabled,
  }) => {
        'farmer_id': 'FARMER-1',
        'kyc_status': kycStatus,
        'transaction_enabled': transactionEnabled,
        'live_listings': 0,
        'active_offers': 0,
        'settled_amount_paise': 0,
      };

  test('verified Farmer dashboard enables transaction UI', () {
    final model = FarmerDashboard.fromJson(
      dashboard(kycStatus: 'KYC_VERIFIED', transactionEnabled: true),
    );
    expect(model.transactionEnabled, isTrue);
  });

  test('pending Farmer dashboard keeps transaction UI disabled', () {
    final model = FarmerDashboard.fromJson(
      dashboard(kycStatus: 'KYC_PENDING', transactionEnabled: false),
    );
    expect(model.transactionEnabled, isFalse);
  });

  test('rejects inconsistent KYC transaction boundary', () {
    expect(
      () => FarmerDashboard.fromJson(
        dashboard(kycStatus: 'KYC_PENDING', transactionEnabled: true),
      ),
      throwsA(isA<FormatException>()),
    );
    expect(
      () => FarmerDashboard.fromJson(
        dashboard(kycStatus: 'KYC_VERIFIED', transactionEnabled: false),
      ),
      throwsA(isA<FormatException>()),
    );
  });

  test('rejects negative authoritative dashboard counters', () {
    final json = dashboard(
      kycStatus: 'KYC_PENDING',
      transactionEnabled: false,
    )..['live_listings'] = -1;
    expect(
      () => FarmerDashboard.fromJson(json),
      throwsA(isA<FormatException>()),
    );
  });
}
