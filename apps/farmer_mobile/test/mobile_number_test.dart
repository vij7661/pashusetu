import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/app.dart';
import 'package:pashusetu_farmer/src/features/auth/mobile_number.dart';
import 'package:shared_preferences/shared_preferences.dart';

Future<void> _openRegistration(WidgetTester tester) async {
  SharedPreferences.setMockInitialValues({});
  await tester.pumpWidget(const ProviderScope(child: PashuSetuFarmerApp()));
  await tester.pumpAndSettle();
  await tester.tap(find.byType(DropdownButtonFormField<String>));
  await tester.pumpAndSettle();
  await tester.tap(find.text('English').last);
  await tester.pumpAndSettle();
  await tester.tap(find.text('New Farmer Registration'));
  await tester.pumpAndSettle();
}

void main() {
  test('only an exact 10-digit local mobile number is valid', () {
    expect(isValidMobileNumber('9876543210'), isTrue);
    expect(toIndiaE164('9876543210'), '+919876543210');
    expect(isValidMobileNumber('987654321'), isFalse);
    expect(isValidMobileNumber('98765432101'), isFalse);
    expect(isValidMobileNumber('+919876543210'), isFalse);
    expect(isValidMobileNumber('98765 43210'), isFalse);
    expect(isValidMobileNumber('abcdefghij'), isFalse);
  });

  testWidgets('fresh registration is empty and rejects a short number', (
    tester,
  ) async {
    await _openRegistration(tester);
    final field = find.byType(TextField).first;
    expect(tester.widget<TextField>(field).controller!.text, isEmpty);

    await tester.enterText(field, '987654321');
    await tester.tap(find.text('Continue'));
    await tester.pump();

    expect(find.text('Invalid mobile number'), findsOneWidget);
    expect(find.text('Mobile Verification'), findsOneWidget);
  });

  testWidgets('mobile field filters malformed input and limits it to 10 digits',
      (
    tester,
  ) async {
    await _openRegistration(tester);
    final field = find.byType(TextField).first;

    await tester.enterText(field, '98ab76-5432101');
    await tester.pump();

    expect(tester.widget<TextField>(field).controller!.text, '9876543210');
  });
}
