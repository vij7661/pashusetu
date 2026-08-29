import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/localization/app_strings.dart';
import 'package:pashusetu_farmer/src/core/localization/marketplace_strings.dart';

void main() {
  test('marketplace status labels exist for every supported language', () {
    final englishKeys = MarketplaceStrings.values['en']!.keys.toSet();
    for (final language in AppStrings.supportedLanguages) {
      final strings = MarketplaceStrings.values[language];
      expect(strings, isNotNull);
      expect(strings!.keys.toSet(), englishKeys);
      for (final key in englishKeys) {
        expect(strings[key]!.trim(), isNotEmpty);
      }
    }
  });

  test('unknown listing statuses remain visible instead of being hidden', () {
    expect(MarketplaceStrings.listingStatus('en', 'REVIEW'), 'REVIEW');
  });
}
