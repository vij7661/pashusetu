import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:pashusetu_farmer/src/core/api/api_client.dart';
import 'package:pashusetu_farmer/src/core/api/token_store.dart';
import 'package:pashusetu_farmer/src/features/livestock/create_livestock_screen.dart';
import 'package:pashusetu_farmer/src/features/livestock/livestock_models.dart';
import 'package:pashusetu_farmer/src/features/livestock/livestock_repository.dart';
import 'package:pashusetu_farmer/src/features/providers.dart';

class FakeLivestockRepository extends LivestockRepository {
  FakeLivestockRepository() : super(ApiClient(TokenStore()));

  int goatCalls = 0;
  int lotCalls = 0;
  Object? goatError;
  final goatCompleter = Completer<Goat>();

  @override
  Future<Goat> createGoat({
    String? breed,
    String? sex,
    int? ageMonths,
    String? healthNotes,
  }) async {
    goatCalls++;
    if (goatError case final error?) throw error;
    return goatCompleter.future;
  }

  @override
  Future<Lot> createLot({
    required int quantity,
    String? breedSummary,
    String? sexSummary,
    String? ageSummary,
    List<String> goatIds = const [],
  }) async {
    lotCalls++;
    return Lot(
      id: 'PS-L-QA000001',
      declaredQuantity: quantity,
      linkedGoatIds: const [],
      status: 'DRAFT',
      breedSummary: breedSummary,
    );
  }
}

Future<void> pumpFlow(
  WidgetTester tester,
  FakeLivestockRepository repository,
) async {
  final router = GoRouter(
    initialLocation: '/livestock/new',
    routes: [
      GoRoute(
        path: '/livestock/new',
        builder: (_, __) => const CreateLivestockScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (_, __) => const Scaffold(body: Text('QA Home')),
      ),
    ],
  );
  await tester.pumpWidget(
    ProviderScope(
      overrides: [livestockRepositoryProvider.overrideWithValue(repository)],
      child: MaterialApp.router(routerConfig: router),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('successful goat submit is single-call and navigates Home', (
    tester,
  ) async {
    final repository = FakeLivestockRepository();
    await pumpFlow(tester, repository);
    await tester.enterText(find.byType(TextField), 'Deccani');
    await tester.tap(find.text('Add Individual Goat'));
    await tester.pump();
    expect(repository.goatCalls, 1);
    expect(tester.widget<FilledButton>(find.byType(FilledButton)).onPressed,
        isNull);

    repository.goatCompleter.complete(
      Goat(id: 'PS-G-QA000001', status: 'DRAFT', breed: 'Deccani', sex: 'MALE'),
    );
    await tester.pumpAndSettle();
    expect(repository.goatCalls, 1);
    expect(find.text('QA Home'), findsOneWidget);
    expect(find.textContaining('Goat added successfully.'), findsOneWidget);
  });

  testWidgets('goat API failure stays recoverable with safe message', (
    tester,
  ) async {
    final repository = FakeLivestockRepository()
      ..goatError =
          const ApiException('API_ERROR', 'Internal detail', statusCode: 500);
    await pumpFlow(tester, repository);
    await tester.tap(find.text('Add Individual Goat'));
    await tester.pumpAndSettle();
    expect(find.text('Server error. Please try again later.'), findsOneWidget);
    expect(find.textContaining('API_ERROR'), findsNothing);
    expect(find.text('Add Goat / Create Lot'), findsOneWidget);
  });

  testWidgets('Lot creation remains on its existing result state', (
    tester,
  ) async {
    final repository = FakeLivestockRepository();
    await pumpFlow(tester, repository);
    await tester.tap(find.text('Multiple Goats / Lot'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField).last, '3');
    await tester.tap(find.text('Create Lot'));
    await tester.pumpAndSettle();
    expect(repository.lotCalls, 1);
    expect(find.text('Lot PS-L-QA000001'), findsOneWidget);
    expect(find.text('QA Home'), findsNothing);
  });
}
