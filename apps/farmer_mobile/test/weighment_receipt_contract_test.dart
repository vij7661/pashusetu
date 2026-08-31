import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/weighment/weighment_models.dart';

void main() {
  test('weighment receipt carries verified listing target', () {
    final receipt = WeighmentReceipt.fromJson({
      'receipt_id': 'receipt-1',
      'receipt_code': 'PS-RCP-001',
      'print_status': 'PRINTED',
      'target_type': 'GOAT',
      'target_id': 'PS-GT-001',
    });

    expect(receipt.targetType, 'GOAT');
    expect(receipt.targetId, 'PS-GT-001');
    expect(receipt.receiptCode, 'PS-RCP-001');
  });

  test('weighment receipt rejects unknown target type', () {
    expect(
      () => WeighmentReceipt.fromJson({
        'receipt_id': 'receipt-1',
        'receipt_code': 'PS-RCP-001',
        'print_status': 'PRINTED',
        'target_type': 'UNKNOWN',
        'target_id': 'PS-GT-001',
      }),
      throwsFormatException,
    );
  });
}
