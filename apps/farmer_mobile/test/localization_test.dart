import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/localization/app_strings.dart';
import 'package:pashusetu_farmer/src/core/localization/language_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('AppStrings', () {
    test('Telugu contains every English localization key', () {
      final englishKeys = AppStrings.values['en']!.keys.toSet();
      final teluguKeys = AppStrings.values['te']!.keys.toSet();

      expect(teluguKeys, englishKeys);
    });

    test('representative farmer flow labels resolve to Telugu', () {
      expect(AppStrings.tr('te', 'farmer_details'), 'రైతు వివరాలు');
      expect(AppStrings.tr('te', 'add_goat_lot'),
          'మేకను జోడించండి / లాట్ సృష్టించండి');
      expect(AppStrings.tr('te', 'buyer_offers'), 'కొనుగోలుదారుల ఆఫర్లు');
      expect(AppStrings.tr('te', 'farmer_acknowledgement'), 'రైతు అంగీకారం');
    });

    test('unknown language falls back to English', () {
      expect(AppStrings.tr('xx', 'farmer_details'), 'Farmer Details');
    });
  });

  group('LanguageController', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('persists a supported language selection', () async {
      final controller = LanguageController();

      await controller.setLanguage('te');

      expect(controller.state, 'te');
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('farmer_language'), 'te');
    });

    test('rejects unsupported languages', () async {
      final controller = LanguageController();

      await controller.setLanguage('xx');

      expect(controller.state, 'en');
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('farmer_language'), isNull);
    });
  });
}
