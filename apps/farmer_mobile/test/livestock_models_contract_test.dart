import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/livestock/livestock_models.dart';

void main() {
  test('goat response validates sex and age', () {
    final goat = Goat.fromJson({
      'goat_id': 'PS-G-1',
      'status': 'DRAFT',
      'breed': null,
      'sex': 'MALE',
      'age_months': 18,
      'health_notes': null,
    });
    expect(goat.sex, 'MALE');

    expect(
      () => Goat.fromJson({
        'goat_id': 'PS-G-1',
        'status': 'DRAFT',
        'breed': null,
        'sex': 'INVALID',
        'age_months': 18,
        'health_notes': null,
      }),
      throwsA(isA<FormatException>()),
    );
  });

  test('lot response rejects impossible linked quantity', () {
    expect(
      () => Lot.fromJson({
        'lot_id': 'PS-L-1',
        'declared_quantity': 1,
        'linked_goat_ids': ['PS-G-1', 'PS-G-2'],
        'status': 'DRAFT',
        'breed_summary': null,
      }),
      throwsA(isA<FormatException>()),
    );
  });

  test('lot response requires valid positive quantity and identifiers', () {
    final lot = Lot.fromJson({
      'lot_id': 'PS-L-1',
      'declared_quantity': 2,
      'linked_goat_ids': ['PS-G-1'],
      'status': 'DRAFT',
      'breed_summary': null,
    });
    expect(lot.declaredQuantity, 2);

    expect(
      () => Lot.fromJson({
        'lot_id': 'PS-L-1',
        'declared_quantity': 0,
        'linked_goat_ids': <String>[],
        'status': 'DRAFT',
        'breed_summary': null,
      }),
      throwsA(isA<FormatException>()),
    );
  });
}
