import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/localization/app_strings.dart';

void main() {
  test('golden-path listing and offer labels exist in English and Telugu', () {
    for (final language in ['en', 'te']) {
      expect(AppStrings.tr(language, 'your_listings'), isNotEmpty);
      expect(AppStrings.tr(language, 'no_listings'), isNotEmpty);
      expect(AppStrings.tr(language, 'buyer_offers'), isNotEmpty);
      expect(AppStrings.tr(language, 'accept'), isNotEmpty);
    }
  });
}
