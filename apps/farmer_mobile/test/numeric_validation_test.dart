import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/shared/numeric_validation.dart';

void main() {
  test('lot quantity enforces below exact and above boundaries', () {
    expect(isValidLotQuantity(''), isFalse);
    expect(isValidLotQuantity('0'), isFalse);
    expect(isValidLotQuantity('1'), isTrue);
    expect(isValidLotQuantity('500'), isTrue);
    expect(isValidLotQuantity('501'), isFalse);
    expect(isValidLotQuantity('-1'), isFalse);
    expect(isValidLotQuantity('1.5'), isFalse);
    expect(isValidLotQuantity(' 3 '), isFalse);
    expect(isValidLotQuantity('3goats'), isFalse);
  });

  test('listing price must be a positive whole-rupee value', () {
    expect(isValidPositivePrice(''), isFalse);
    expect(isValidPositivePrice('0'), isFalse);
    expect(isValidPositivePrice('1'), isTrue);
    expect(isValidPositivePrice('400'), isTrue);
    expect(isValidPositivePrice('-1'), isFalse);
    expect(isValidPositivePrice('1.5'), isFalse);
    expect(isValidPositivePrice(' 400 '), isFalse);
  });

  test('agreement and dispute boundaries follow backend contracts', () {
    expect(isValidAgreementLocation('ab'), isFalse);
    expect(isValidAgreementLocation(' QA Centre '), isTrue);
    expect(isApprovedTolerance('1.4'), isFalse);
    expect(isApprovedTolerance('1.5'), isTrue);
    expect(isApprovedTolerance('1.6'), isFalse);
    expect(isValidNonNegativeAmount(''), isFalse);
    expect(isValidNonNegativeAmount('0'), isTrue);
    expect(isValidNonNegativeAmount('1'), isTrue);
    expect(isValidNonNegativeAmount('-1'), isFalse);
    expect(isValidNonNegativeAmount('1.5'), isFalse);
  });
}
