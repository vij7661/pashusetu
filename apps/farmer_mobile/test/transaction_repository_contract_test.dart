import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/api/api_client.dart';
import 'package:pashusetu_farmer/src/core/api/token_store.dart';
import 'package:pashusetu_farmer/src/features/transaction/transaction_repository.dart';

class _RecordingApiClient extends ApiClient {
  _RecordingApiClient() : super(TokenStore());

  String? lastGetPath;
  String? lastPostPath;

  @override
  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, dynamic>? query,
  }) async {
    lastGetPath = path;
    return {
      'settlement_id': 'SET-001',
      'gross_amount_paise': 100000,
      'adjustment_paise': 0,
      'platform_fee_paise': 1000,
      'final_amount_paise': 99000,
      'status': 'SETTLED',
    };
  }

  @override
  Future<Map<String, dynamic>> post(
    String path, {
    Map<String, dynamic>? body,
    Map<String, dynamic>? headers,
  }) async {
    lastPostPath = path;
    throw StateError('Settlement read must not use POST');
  }
}

void main() {
  test('farmer settlement repository is read-only and uses GET', () async {
    final api = _RecordingApiClient();
    final repository = TransactionRepository(api);

    final settlement = await repository.settlement('TX-001');

    expect(api.lastGetPath, '/payments/transactions/TX-001/settlement');
    expect(api.lastPostPath, isNull);
    expect(settlement.id, 'SET-001');
    expect(settlement.finalAmountPaise, 99000);
  });
}
