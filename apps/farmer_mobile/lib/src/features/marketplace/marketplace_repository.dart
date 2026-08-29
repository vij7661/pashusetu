import '../../core/api/api_client.dart';
import 'marketplace_models.dart';

class MarketplaceRepository {
  MarketplaceRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> listingContext({
    required String targetType,
    required String targetId,
  }) {
    return _api.get('/marketplace/listing-context', query: {
      'target_type': targetType,
      'target_id': targetId,
    });
  }

  Future<List<Map<String, dynamic>>> recommendations(String marketCode) async {
    final rows = await _api.getList('/marketplace/recommendations', query: {
      'market_code': marketCode,
    });
    return rows.cast<Map<String, dynamic>>();
  }

  Future<Listing> createListing({
    required String targetType,
    required String targetId,
    required int pricePerKgPaise,
    required DateTime opensAt,
    required DateTime closesAt,
    String? recommendationId,
  }) async {
    final json = await _api.post('/marketplace/listings', body: {
      'target_type': targetType,
      'target_id': targetId,
      'farmer_price_per_kg_paise': pricePerKgPaise,
      'farmer_acknowledged': true,
      'sale_type': 'COMPETITIVE_BIDDING',
      'opens_at': opensAt.toUtc().toIso8601String(),
      'closes_at': closesAt.toUtc().toIso8601String(),
      'recommendation_id': recommendationId,
    });
    return Listing.fromJson(json);
  }

  Future<List<Listing>> myListings() async {
    final rows = await _api.getList('/marketplace/listings');
    return rows
        .map((e) => Listing.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<BidOffer>> bids(String listingId) async {
    final rows = await _api.getList('/bidding/listings/$listingId/bids');
    return rows
        .map((e) => BidOffer.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Map<String, dynamic>> acceptBid(String listingId, String bidId) {
    return _api.post('/bidding/listings/$listingId/accept/$bidId');
  }
}
