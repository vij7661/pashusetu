import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/weighment/weighment_models.dart';
import 'package:pashusetu_farmer/src/features/weighment/weighment_strings.dart';

void main() {
  test('parses accepted Farmer weighment decision', () {
    final decision = WeighmentDecision.fromJson({
      'acknowledgement_id': 'ack-1',
      'status': 'ACKNOWLEDGED',
    });

    expect(decision.accepted, isTrue);
    expect(decision.rejected, isFalse);
    expect(decision.acknowledgementId, 'ack-1');
  });

  test('parses rejected Farmer weighment decision without acknowledgement id', () {
    final decision = WeighmentDecision.fromJson({
      'acknowledgement_id': null,
      'status': 'REJECTED_BY_FARMER',
    });

    expect(decision.accepted, isFalse);
    expect(decision.rejected, isTrue);
    expect(decision.acknowledgementId, isNull);
  });

  test('rejects inconsistent Farmer weighment decision payload', () {
    expect(
      () => WeighmentDecision.fromJson({
        'acknowledgement_id': null,
        'status': 'ACKNOWLEDGED',
      }),
      throwsA(isA<FormatException>()),
    );
    expect(
      () => WeighmentDecision.fromJson({
        'acknowledgement_id': 'ack-1',
        'status': 'REJECTED_BY_FARMER',
      }),
      throwsA(isA<FormatException>()),
    );
  });

  test('weighment rejection guidance exists in all Farmer languages', () {
    for (final language in const ['te', 'hi', 'en', 'mr', 'ta', 'ml']) {
      expect(WeighmentStrings.tr(language, 'reject_weight').trim(), isNotEmpty);
      expect(WeighmentStrings.tr(language, 'reweigh_required').trim(), isNotEmpty);
    }
  });
}
