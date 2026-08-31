import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/marketplace/marketplace_models.dart';

void main() {
  test('listing context requires authoritative weight and market', () {
    final context = ListingContext.fromJson({
      'target_type': 'LOT',
      'target_id': 'lot-1',
      'verified_weight_kg': '50.125',
      'market_code': 'HYDERABAD',
    });

    expect(context.verifiedWeightKg, 50.125);
    expect(context.marketCode, 'HYDERABAD');
    expect(
      () => ListingContext.fromJson({
        'target_type': 'LOT',
        'target_id': 'lot-1',
        'verified_weight_kg': 'not-a-weight',
        'market_code': 'HYDERABAD',
      }),
      throwsA(isA<FormatException>()),
    );
  });

  test('market recommendation validates provenance dates', () {
    final reference = MarketRecommendation.fromJson({
      'recommendation_id': 'ref-1',
      'market_code': 'HYDERABAD',
      'breed': null,
      'price_per_kg_paise': 40000,
      'source_label': 'Admin field reference',
      'valid_from': '2026-08-31T00:00:00Z',
      'valid_to': null,
    });

    expect(reference.pricePerKgPaise, 40000);
    expect(reference.sourceLabel, 'Admin field reference');
    expect(
      () => MarketRecommendation.fromJson({
        'recommendation_id': 'ref-1',
        'market_code': 'HYDERABAD',
        'breed': null,
        'price_per_kg_paise': 40000,
        'source_label': 'Admin field reference',
        'valid_from': 'invalid-date',
        'valid_to': null,
      }),
      throwsA(isA<FormatException>()),
    );
  });

  test('bid acceptance is a typed authoritative response', () {
    final acceptance = BidAcceptance.fromJson({
      'listing_id': 'listing-1',
      'accepted_bid_id': 'bid-1',
      'accepted_server_sequence': 17,
      'status': 'ACCEPTED',
    });

    expect(acceptance.acceptedBidId, 'bid-1');
    expect(acceptance.acceptedServerSequence, 17);
    expect(acceptance.status, 'ACCEPTED');
  });
}
