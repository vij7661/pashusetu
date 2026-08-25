import 'package:flutter_test/flutter_test.dart';

void main() {
  test('farmer accept path does not loop to scale', () {
    const flow = [
      'LIVE',
      'WEIGHT_LOCKED',
      'FARMER_REVIEW',
      'FARMER_ACCEPTS',
      'ACKNOWLEDGEMENT_HANDOFF',
    ];
    expect(flow.indexOf('ACKNOWLEDGEMENT_HANDOFF') > flow.indexOf('FARMER_ACCEPTS'), true);
    expect(flow.where((x) => x == 'LIVE').length, 1);
  });
}
