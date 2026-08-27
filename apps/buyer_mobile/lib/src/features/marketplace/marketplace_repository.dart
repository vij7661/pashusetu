import '../../core/api/api_client.dart';

class MarketplaceRepository {
  MarketplaceRepository(this._api);
  final ApiClient _api;

  Future<List<Map<String, dynamic>>> search({
    required int requiredQuantity,
    required double latitude,
    required double longitude,
    double? minWeightKg,
    double? maxWeightKg,
  }) async {
    final rows = await _api.getList('/marketplace/listings', query: {
      'required_quantity': requiredQuantity,
      'search_latitude': latitude,
      'search_longitude': longitude,
      if (minWeightKg != null) 'min_weight_kg': minWeightKg,
      if (maxWeightKg != null) 'max_weight_kg': maxWeightKg,
    });
    return rows.cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> bid({
    required String listingId,
    required int pricePerKgPaise,
    required String idempotencyKey,
    required List<String> selectedGoatIds,
    required bool wholeLot,
  }) =>
      _api.post(
        '/bidding/listings/$listingId/bids',
        body: {
          'price_per_kg_paise': pricePerKgPaise,
          'selected_goat_ids': selectedGoatIds,
          'whole_lot': wholeLot,
        },
        headers: {'Idempotency-Key': idempotencyKey},
      );

  Future<List<Map<String, dynamic>>> bids(String listingId) async {
    final rows = await _api.getList('/bidding/listings/$listingId/bids');
    return rows.cast<Map<String, dynamic>>();
  }
}
