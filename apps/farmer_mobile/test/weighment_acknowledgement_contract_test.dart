import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/weighment/weighment_models.dart';

void main() {
  test('parses Farmer acknowledgement response', () {
    final acknowledgement = WeighmentAcknowledgement.fromJson({
      'acknowledgement_id': 'ack-1',
      'status': 'ACKNOWLEDGED_BY_FARMER',
    });

    expect(acknowledgement.acknowledgementId, 'ack-1');
    expect(acknowledgement.status, 'ACKNOWLEDGED_BY_FARMER');
  });

  test('rejects unexpected Farmer acknowledgement status', () {
    expect(
      () => WeighmentAcknowledgement.fromJson({
        'acknowledgement_id': 'ack-1',
        'status': 'VERIFIED',
      }),
      throwsA(isA<FormatException>()),
    );
  });
}
