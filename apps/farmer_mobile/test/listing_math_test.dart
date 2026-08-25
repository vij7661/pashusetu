import 'package:flutter_test/flutter_test.dart';

void main() {
  test('50kg x 400 rupees is 20,000 rupees', () {
    const weightKg = 50.0;
    const pricePerKgPaise = 40000;
    final totalPaise = (weightKg * pricePerKgPaise).round();
    expect(totalPaise, 2000000);
  });

  test('50kg x 492 rupees is 24,600 rupees', () {
    const weightKg = 50.0;
    const pricePerKgPaise = 49200;
    final totalPaise = (weightKg * pricePerKgPaise).round();
    expect(totalPaise, 2460000);
  });
}
