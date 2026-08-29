import 'package:flutter/services.dart';

bool isValidLotQuantity(String value) {
  final parsed = int.tryParse(value);
  return RegExp(r'^\d{1,3}$').hasMatch(value) &&
      parsed != null &&
      parsed >= 1 &&
      parsed <= 500;
}

bool isValidPositivePrice(String value) {
  final parsed = int.tryParse(value);
  return RegExp(r'^\d+$').hasMatch(value) && parsed != null && parsed > 0;
}

bool isValidNonNegativeAmount(String value) =>
    RegExp(r'^\d+$').hasMatch(value) && int.tryParse(value) != null;

bool isValidAgreementLocation(String value) {
  final length = value.trim().length;
  return length >= 3 && length <= 255;
}

bool isApprovedTolerance(String value) => double.tryParse(value) == 1.5;

class RejectingDigitsFormatter extends TextInputFormatter {
  const RejectingDigitsFormatter({this.maxLength});

  final int? maxLength;

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    if (!RegExp(r'^\d*$').hasMatch(newValue.text) ||
        (maxLength != null && newValue.text.length > maxLength!)) {
      return oldValue;
    }
    return newValue;
  }
}
