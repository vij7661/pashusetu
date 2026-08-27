import 'package:flutter/services.dart';

const int mobileNumberLength = 10;

bool isValidMobileNumber(String value) =>
    RegExp(r'^[6-9][0-9]{9}$').hasMatch(value);

String toIndiaE164(String value) => '+91$value';

class MobileNumberInputFormatter extends TextInputFormatter {
  const MobileNumberInputFormatter();

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    if (newValue.text.length > mobileNumberLength ||
        !RegExp(r'^\d*$').hasMatch(newValue.text)) {
      return oldValue;
    }
    return newValue;
  }
}
