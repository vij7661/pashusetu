import '../../core/api/api_client.dart';

class MarketplaceRepository {
  MarketplaceRepository(this._api);
  final ApiClient _api;

  Future<List<Map<String, dynamic>>> search({
    double? minWeightKg,
    double? maxWeightKg,
  }) async {
    final rows = await _api.getList('/marketplace/listings', query: {
      if (minWeightKg != null) 'min_weight_kg': minWeightKg,
      if (maxWeightKg != null) 'max_weight_kg': maxWeightKg,
    });
    return rows.cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> bid({
    required String listingId,
    required int pricePerKgPaise,
    required String idempotencyKey,
  }) =>
      _api.post(
        '/bidding/listings/$listingId/bids',
        body: {'price_per_kg_paise': pricePerKgPaise},
        headers: {'Idempotency-Key': idempotencyKey},
      );

  Future<List<Map<String, dynamic>>> bids(String listingId) async {
    final rows = await _api.getList('/bidding/listings/$listingId/bids');
    return rows.cast<Map<String, dynamic>>();
  }
}
