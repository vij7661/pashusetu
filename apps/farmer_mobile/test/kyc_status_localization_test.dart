import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/core/localization/app_strings.dart';
import 'package:pashusetu_farmer/src/core/localization/kyc_status_strings.dart';

void main() {
  test('KYC status strings exist for every supported Farmer language', () {
    const requiredKeys = {
      'verified',
      'pending',
      'action_required',
      'rejected',
      'incomplete',
      'transaction_note',
      'available_after_kyc',
      'dashboard_state_error',
    };

    for (final language in AppStrings.supportedLanguages) {
      final strings = KycStatusStrings.values[language];
      expect(strings, isNotNull, reason: 'Missing KYC localization for $language');
      expect(strings!.keys.toSet(), requiredKeys);
      for (final key in requiredKeys) {
        expect(strings[key]!.trim(), isNotEmpty);
      }
      expect(
        KycStatusStrings.statusLabel(language, 'KYC_VERIFIED').trim(),
        isNotEmpty,
      );
    }
  });
}
