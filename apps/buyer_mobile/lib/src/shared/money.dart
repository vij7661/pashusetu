import 'package:intl/intl.dart';

final _currency = NumberFormat.currency(locale: 'en_IN', symbol: '₹', decimalDigits: 0);
String formatPaise(int paise) => _currency.format(paise / 100);
