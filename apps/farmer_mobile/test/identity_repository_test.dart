import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/api/api_client.dart';
import 'package:pashusetu_farmer/src/core/api/token_store.dart';
import 'package:pashusetu_farmer/src/features/identity/identity_repository.dart';

class CapturingApiClient extends ApiClient {
  CapturingApiClient() : super(TokenStore());

  String? path;
  Map<String, dynamic>? body;

  @override
  Future<Map<String, dynamic>> post(
    String path, {
    Map<String, dynamic>? body,
    Map<String, dynamic>? headers,
  }) async {
    this.path = path;
    this.body = body;
    return {
      'farmer_id': 'FARMER_TE_001',
      'kyc_status': 'QA_VERIFIED',
      'kyc_masked_id': 'XXXXXXXX8847',
      'payout_status': 'QA_CONFIGURED',
      'payout_masked_reference': 'XXXXXXXX9012',
    };
  }
}

void main() {
  test('final submit uses the exact browser wizard JSON shape', () async {
    final api = CapturingApiClient();
    final repository = IdentityRepository(api);
    final result = await repository.createFarmer(
      fullName: 'Synthetic Telugu Farmer',
      language: 'te',
      village: 'QA Village',
      mandal: 'QA Mandal',
      district: 'QA District',
      kyc: {
        'aadhaar_number': '999971658847',
        'name_as_per_aadhaar': 'Kumar Agarwal',
        'consent': true,
      },
      payout: {
        'method': 'BANK',
        'account_holder_name': 'Kumar Agarwal',
        'account_number': '123456789012',
        'confirm_account_number': '123456789012',
        'ifsc': 'HDFC0001234',
      },
    );

    expect(api.path, '/identity/farmers');
    expect(
        api.body!.keys,
        containsAll([
          'full_name',
          'village',
          'mandal',
          'district',
          'state',
          'preferred_language',
          'kyc',
          'payout',
        ]));
    expect((api.body!['kyc'] as Map).keys,
        containsAll(['aadhaar_number', 'name_as_per_aadhaar', 'consent']));
    expect(
        (api.body!['payout'] as Map).keys,
        containsAll([
          'method',
          'account_holder_name',
          'account_number',
          'confirm_account_number',
          'ifsc',
        ]));
    expect(result['kyc_masked_id'], 'XXXXXXXX8847');
    expect(result['payout_masked_reference'], 'XXXXXXXX9012');
  });
}
