import 'package:flutter/services.dart';

class AadhaarInputFormatter extends TextInputFormatter {
  const AadhaarInputFormatter();

  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    final digits = newValue.text.replaceAll(RegExp(r'\D'), '');
    final value = digits.length > 12 ? digits.substring(0, 12) : digits;
    return TextEditingValue(
        text: value, selection: TextSelection.collapsed(offset: value.length));
  }
}

class AccountNumberInputFormatter extends TextInputFormatter {
  const AccountNumberInputFormatter();

  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    final digits = newValue.text.replaceAll(RegExp(r'\D'), '');
    final value = digits.length > 18 ? digits.substring(0, 18) : digits;
    return TextEditingValue(
        text: value, selection: TextSelection.collapsed(offset: value.length));
  }
}

bool isValidAadhaar(String value) => RegExp(r'^\d{12}$').hasMatch(value.trim());
bool isValidKycName(String value) =>
    value.trim().length >= 2 && value.trim().length <= 120;
bool isValidUpi(String value) =>
    RegExp(r'^[A-Za-z0-9._-]{2,}@[A-Za-z0-9.-]{2,}$').hasMatch(value.trim());
bool isValidAccountNumber(String value) =>
    RegExp(r'^\d{6,18}$').hasMatch(value.trim());
bool isValidIfsc(String value) =>
    RegExp(r'^[A-Z]{4}0[A-Z0-9]{6}$').hasMatch(value.trim().toUpperCase());

String maskedAadhaar(String value) =>
    'XXXXXXXX${value.substring(value.length - 4)}';
String maskedAccount(String value) =>
    'XXXXXXXX${value.substring(value.length - 4)}';
