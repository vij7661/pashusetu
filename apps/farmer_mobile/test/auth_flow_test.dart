import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/app.dart';
import 'package:pashusetu_farmer/src/core/api/api_client.dart';
import 'package:pashusetu_farmer/src/core/api/token_store.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_controller.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_models.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_repository.dart';
import 'package:shared_preferences/shared_preferences.dart';

class FakeAuthRepository extends AuthRepository {
  FakeAuthRepository() : super(ApiClient(TokenStore()), TokenStore());

  int requestCalls = 0;
  int verifyCalls = 0;

  @override
  Future<void> requestOtp(String mobile) async {
    requestCalls++;
  }

  @override
  Future<TokenPair> verifyOtp(String mobile, String otp) async {
    verifyCalls++;
    if (otp != '4816') {
      throw const ApiException('OTP_INVALID', 'Invalid OTP.', statusCode: 400);
    }
    return TokenPair(accessToken: 'qa-access', refreshToken: 'qa-refresh');
  }
}

Future<void> _openEnglishLogin(
  WidgetTester tester,
  FakeAuthRepository repository,
) async {
  SharedPreferences.setMockInitialValues({});
  await tester.pumpWidget(
    ProviderScope(
      overrides: [authRepositoryProvider.overrideWithValue(repository)],
      child: const PashuSetuFarmerApp(),
    ),
  );
  await tester.pumpAndSettle();
  await tester.tap(find.byType(DropdownButtonFormField<String>));
  await tester.pumpAndSettle();
  await tester.tap(find.text('English').last);
  await tester.pumpAndSettle();
  await tester.tap(find.text('Existing Customer Login'));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('invalid mobile and malformed OTP never call auth API', (
    tester,
  ) async {
    final repository = FakeAuthRepository();
    await _openEnglishLogin(tester, repository);

    await tester.enterText(find.byType(TextField).first, '612345678');
    await tester.tap(find.text('Send OTP'));
    await tester.pump();
    expect(find.text('Invalid mobile number'), findsOneWidget);
    expect(repository.requestCalls, 0);

    await tester.enterText(find.byType(TextField).first, '6123456789');
    await tester.tap(find.text('Send OTP'));
    await tester.pumpAndSettle();
    expect(repository.requestCalls, 1);

    await tester.enterText(find.byType(TextField).last, '12');
    await tester.tap(find.text('Login & Go to Home'));
    await tester.pump();
    expect(find.text('Enter a valid OTP'), findsOneWidget);
    expect(repository.verifyCalls, 0);
  });

  testWidgets(
      'wrong OTP stays on login without technical leak then correct OTP navigates',
      (
    tester,
  ) async {
    final repository = FakeAuthRepository();
    await _openEnglishLogin(tester, repository);
    await tester.enterText(find.byType(TextField).first, '6123456789');
    await tester.tap(find.text('Send OTP'));
    await tester.pumpAndSettle();

    await tester.enterText(find.byType(TextField).last, '0000');
    await tester.tap(find.text('Login & Go to Home'));
    await tester.pumpAndSettle();
    expect(
        find.text('The OTP is incorrect. Please try again.'), findsOneWidget);
    expect(find.textContaining('DioException'), findsNothing);
    expect(find.textContaining('OTP_INVALID'), findsNothing);
    expect(find.text('Existing Farmer Login'), findsOneWidget);

    await tester.enterText(find.byType(TextField).last, '4816');
    await tester.tap(find.text('Login & Go to Home'));
    await tester.pumpAndSettle();
    expect(find.text('Farmer Dashboard'), findsOneWidget);
    expect(repository.verifyCalls, 2);
  });
}
