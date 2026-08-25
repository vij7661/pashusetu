import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/shared/money.dart';

void main() {
  test('formats paise to rupees', () {
    expect(formatPaise(2000000), contains('20,000'));
  });
}
