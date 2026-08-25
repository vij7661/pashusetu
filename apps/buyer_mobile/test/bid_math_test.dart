import 'package:flutter_test/flutter_test.dart';

void main() {
  test('50kg x Rs492 is Rs24600', () {
    const weight = 50.0;
    const pricePaise = 49200;
    expect((weight * pricePaise).round(), 2460000);
  });
}
