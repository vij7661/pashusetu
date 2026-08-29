import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/identity/onboarding_validation.dart';

void main() {
  test('Aadhaar contract accepts exactly twelve digits', () {
    expect(isValidAadhaar(''), isFalse);
    expect(isValidAadhaar('99997165884'), isFalse);
    expect(isValidAadhaar('999971658847'), isTrue);
    expect(isValidAadhaar('9999716588471'), isFalse);
    expect(isValidAadhaar('99997 1658847'), isFalse);
    expect(isValidAadhaar('99997a658847'), isFalse);
  });

  test('Aadhaar formatter strips paste separators and caps at twelve', () {
    const formatter = AadhaarInputFormatter();
    final result = formatter.formatEditUpdate(
      TextEditingValue.empty,
      const TextEditingValue(text: '9999 7165-8847abc9'),
    );
    expect(result.text, '999971658847');
  });

  test('UPI validation covers blank invalid and valid synthetic handles', () {
    expect(isValidUpi(''), isFalse);
    expect(isValidUpi('farmer'), isFalse);
    expect(isValidUpi('farmer.en@pashusetuqa'), isTrue);
  });

  test('bank validation covers account and IFSC boundaries', () {
    expect(isValidAccountNumber('12345'), isFalse);
    expect(isValidAccountNumber('123456'), isTrue);
    expect(isValidAccountNumber('1234567890123456789'), isFalse);
    expect(isValidIfsc('HDFC0001234'), isTrue);
    expect(isValidIfsc('HDFC001234'), isFalse);
    expect(maskedAccount('123456789012'), 'XXXXXXXX9012');
    expect(maskedAadhaar('999971658847'), 'XXXXXXXX8847');
  });
}
