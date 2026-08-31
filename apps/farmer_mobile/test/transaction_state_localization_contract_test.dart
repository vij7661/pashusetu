import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/transaction/transaction_state_strings.dart';

void main() {
  test('every supported Farmer language covers every backend transaction state', () {
    for (final language in const ['te', 'hi', 'en', 'mr', 'ta', 'ml']) {
      expect(
        TransactionStateStrings.hasCompleteLanguage(language),
        isTrue,
        reason: 'Missing transaction state localization for $language',
      );
      for (final state in TransactionStateStrings.supportedStates) {
        expect(TransactionStateStrings.label(language, state).trim(), isNotEmpty);
      }
    }
  });

  test('known non-English state is not exposed as raw backend code', () {
    expect(
      TransactionStateStrings.label('te', 'IN_TRANSIT'),
      isNot('IN_TRANSIT'),
    );
  });

  test('unknown future state remains visible instead of being hidden', () {
    expect(
      TransactionStateStrings.label('en', 'NEW_FUTURE_STATE'),
      'NEW_FUTURE_STATE',
    );
  });
}
