import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/app.dart';
import 'package:pashusetu_farmer/src/core/api/api_client.dart';
import 'package:pashusetu_farmer/src/core/api/token_store.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_controller.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_models.dart';
import 'package:pashusetu_farmer/src/features/auth/auth_repository.dart';
import 'package:pashusetu_farmer/src/features/identity/identity_repository.dart';
import 'package:pashusetu_farmer/src/features/providers.dart';
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

class FakeIdentityRepository extends IdentityRepository {
  FakeIdentityRepository({this.existingProfile = false})
      : super(ApiClient(TokenStore()));

  final bool existingProfile;

  int verifyKycCalls = 0;
  int createFarmerCalls = 0;

  @override
  Future<bool> hasFarmerProfile() async => existingProfile;

  @override
  Future<Map<String, dynamic>> verifyKyc({
    required String aadhaarNumber,
    required String name,
    required bool consent,
  }) async {
    verifyKycCalls++;
    return {'status': 'QA_VERIFIED', 'masked_id': 'XXXXXXXX8847'};
  }

  @override
  Future<Map<String, dynamic>> createFarmer({
    required String fullName,
    required String language,
    String? village,
    String? mandal,
    String? district,
    required Map<String, dynamic> kyc,
    required Map<String, dynamic> payout,
  }) async {
    createFarmerCalls++;
    return {'farmer_id': 'FARMER_TE_001'};
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
  testWidgets('existing Farmer entering registration routes Home after OTP', (
    tester,
  ) async {
    final auth = FakeAuthRepository();
    final identity = FakeIdentityRepository(existingProfile: true);
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authRepositoryProvider.overrideWithValue(auth),
          identityRepositoryProvider.overrideWithValue(identity),
        ],
        child: const PashuSetuFarmerApp(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byType(DropdownButtonFormField<String>));
    await tester.pumpAndSettle();
    await tester.tap(find.text('English').last);
    await tester.pumpAndSettle();
    await tester.tap(find.text('New Farmer Registration'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), '6123456789');
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), '4816');
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();

    expect(find.text('Farmer Dashboard'), findsOneWidget);
    expect(find.text('Farmer Details'), findsNothing);
    expect(identity.createFarmerCalls, 0);
  });

  testWidgets('new Farmer OTP skips duplicate language and preserves English', (
    tester,
  ) async {
    final repository = FakeAuthRepository();
    final identity = FakeIdentityRepository();
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authRepositoryProvider.overrideWithValue(repository),
          identityRepositoryProvider.overrideWithValue(identity),
        ],
        child: const PashuSetuFarmerApp(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byType(DropdownButtonFormField<String>));
    await tester.pumpAndSettle();
    await tester.tap(find.text('English').last);
    await tester.pumpAndSettle();
    await tester.tap(find.text('New Farmer Registration'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), '7234567890');
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), '4816');
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();

    expect(find.text('Farmer Details'), findsOneWidget);
    expect(find.text('Choose Language'), findsNothing);
    expect(find.text('Full name'), findsOneWidget);

    await tester.enterText(find.byType(TextField).first, 'Kumar Agarwal');
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    expect(find.text('KYC Verification'), findsOneWidget);
    await tester.enterText(find.byType(TextField).first, '999971658847');
    await tester.enterText(find.byType(TextField).last, 'Kumar Agarwal');
    await tester.tap(find.byType(Checkbox));
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    expect(identity.verifyKycCalls, 1);
    expect(find.text('Payout Setup'), findsOneWidget);
    await tester.enterText(find.byType(TextField), 'farmer.en@pashusetuqa');
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    expect(find.text('Review Registration'), findsOneWidget);
    expect(find.textContaining('XXXXXXXX8847'), findsOneWidget);
    await tester.tap(find.byType(Checkbox));
    await tester.tap(find.text('Submit Registration'));
    await tester.pumpAndSettle();
    expect(identity.createFarmerCalls, 1);
    expect(find.text('Farmer Dashboard'), findsOneWidget);
  });

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
