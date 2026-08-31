import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/localization/app_strings.dart';

void main() {
  test('every supported language has the complete Farmer string contract', () {
    final englishKeys = AppStrings.values['en']!.keys.toSet();

    for (final language in AppStrings.supportedLanguages) {
      final strings = AppStrings.values[language];
      expect(strings, isNotNull, reason: 'Missing localization map for $language');
      expect(
        strings!.keys.toSet(),
        englishKeys,
        reason: 'Localization key mismatch for $language',
      );
      for (final key in englishKeys) {
        expect(
          strings[key]!.trim(),
          isNotEmpty,
          reason: 'Empty translation for $language:$key',
        );
      }
    }
  });

  test('pilot pricing is labelled as reference price, not average price', () {
    for (final language in AppStrings.supportedLanguages) {
      final label = AppStrings.values[language]!['market_recommendation']!;
      expect(label.trim(), isNotEmpty);
    }
    expect(AppStrings.values['en']!['market_recommendation'], 'Reference Price');
    expect(
      AppStrings.values['en']!['market_recommendation']!.toLowerCase(),
      isNot(contains('average')),
    );
  });

  test('Farmer-facing localization uses current Setugo product name', () {
    for (final language in AppStrings.supportedLanguages) {
      final connectionError = AppStrings.values[language]!['connection_error']!;
      expect(connectionError, contains('Setugo'));
      expect(connectionError, isNot(contains('PashuSetu')));
    }
  });
}
