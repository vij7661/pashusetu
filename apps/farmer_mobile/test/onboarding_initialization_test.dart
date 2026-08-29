import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/app.dart';
import 'package:pashusetu_farmer/src/core/localization/app_strings.dart';
import 'package:pashusetu_farmer/src/core/localization/language_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

Future<void> _pumpApp(WidgetTester tester) async {
  await tester.pumpWidget(
    const ProviderScope(child: PashuSetuFarmerApp()),
  );
  await tester.pumpAndSettle();
}

Future<void> _selectLanguage(WidgetTester tester, String label) async {
  await tester.tap(find.byType(DropdownButtonFormField<String>));
  await tester.pumpAndSettle();
  await tester.tap(find.text(label).last);
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('fresh state starts at welcome and requires language choice', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});

    await _pumpApp(tester);

    expect(
        find.text('Choose your language / మీ భాషను ఎంచుకోండి'), findsOneWidget);
    expect(find.text(AppStrings.tr('te', 'mobile_verification')), findsNothing);
    expect(find.text('+919876543210'), findsNothing);
    expect(tester.widget<FilledButton>(find.byType(FilledButton)).onPressed,
        isNull);
  });

  testWidgets('explicit English selection drives unseeded English registration',
      (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    await _pumpApp(tester);

    await _selectLanguage(tester, 'English');
    await tester.tap(find.text('New Farmer Registration'));
    await tester.pumpAndSettle();

    expect(
        find.text(AppStrings.tr('en', 'mobile_verification')), findsOneWidget);
    expect(find.text('+919876543210'), findsNothing);
    expect(find.text('4816'), findsNothing);
  });

  testWidgets('explicit Telugu selection drives Telugu registration', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    await _pumpApp(tester);

    await _selectLanguage(tester, 'తెలుగు');
    await tester.tap(find.text('New Farmer Registration'));
    await tester.pumpAndSettle();

    expect(
        find.text(AppStrings.tr('te', 'mobile_verification')), findsOneWidget);
  });

  test('persisted language survives provider recreation', () async {
    SharedPreferences.setMockInitialValues({});
    final first = ProviderContainer();
    await first.read(languageProvider.notifier).setLanguage('te');
    first.dispose();

    final second = ProviderContainer();
    await second.read(languageProvider.notifier).initialized;
    expect(second.read(languageProvider), 'te');
    expect(
      await second.read(languageProvider.notifier).hasPersistedLanguage(),
      isTrue,
    );
    second.dispose();
  });

  testWidgets('persisted locale does not bypass welcome routing',
      (tester) async {
    SharedPreferences.setMockInitialValues({'farmer_language': 'te'});

    await _pumpApp(tester);

    expect(find.text('PashuSetu'), findsOneWidget);
    expect(find.text(AppStrings.tr('te', 'mobile_verification')), findsNothing);
    expect(
      tester.widget<FilledButton>(find.byType(FilledButton)).onPressed,
      isNotNull,
    );
  });
}
