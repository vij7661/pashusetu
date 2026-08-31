class ListingContext {
  const ListingContext({
    required this.targetType,
    required this.targetId,
    required this.verifiedWeightKg,
    required this.marketCode,
  });

  final String targetType;
  final String targetId;
  final double verifiedWeightKg;
  final String marketCode;

  factory ListingContext.fromJson(Map<String, dynamic> json) => ListingContext(
        targetType: json['target_type'] as String,
        targetId: json['target_id'] as String,
        verifiedWeightKg: double.parse(json['verified_weight_kg'].toString()),
        marketCode: json['market_code'] as String,
      );
}

class MarketRecommendation {
  const MarketRecommendation({
    required this.id,
    required this.marketCode,
    required this.pricePerKgPaise,
    required this.sourceLabel,
    required this.validFrom,
    this.breed,
    this.validTo,
  });

  final String id;
  final String marketCode;
  final String? breed;
  final int pricePerKgPaise;
  final String sourceLabel;
  final DateTime validFrom;
  final DateTime? validTo;

  factory MarketRecommendation.fromJson(Map<String, dynamic> json) {
    final validFrom = DateTime.tryParse(json['valid_from']?.toString() ?? '');
    if (validFrom == null) {
      throw const FormatException('Invalid market recommendation valid_from');
    }
    final rawValidTo = json['valid_to'];
    final validTo = rawValidTo == null ? null : DateTime.tryParse(rawValidTo.toString());
    if (rawValidTo != null && validTo == null) {
      throw const FormatException('Invalid market recommendation valid_to');
    }
    return MarketRecommendation(
      id: json['recommendation_id'] as String,
      marketCode: json['market_code'] as String,
      breed: json['breed'] as String?,
      pricePerKgPaise: json['price_per_kg_paise'] as int,
      sourceLabel: json['source_label'] as String,
      validFrom: validFrom,
      validTo: validTo,
    );
  }
}

class BidAcceptance {
  const BidAcceptance({
    required this.listingId,
    required this.acceptedBidId,
    required this.acceptedServerSequence,
    required this.status,
  });

  final String listingId;
  final String acceptedBidId;
  final int acceptedServerSequence;
  final String status;

  factory BidAcceptance.fromJson(Map<String, dynamic> json) => BidAcceptance(
        listingId: json['listing_id'] as String,
        acceptedBidId: json['accepted_bid_id'] as String,
        acceptedServerSequence: json['accepted_server_sequence'] as int,
        status: json['status'] as String,
      );
}

class Listing {
  Listing({
    required this.id,
    required this.targetType,
    required this.verifiedWeightKg,
    required this.pricePerKgPaise,
    required this.totalValuePaise,
    required this.status,
  });

  final String id;
  final String targetType;
  final double verifiedWeightKg;
  final int pricePerKgPaise;
  final int totalValuePaise;
  final String status;

  factory Listing.fromJson(Map<String, dynamic> json) => Listing(
        id: json['listing_id'] as String,
        targetType: json['target_type'] as String,
        verifiedWeightKg: double.parse(json['verified_weight_kg'].toString()),
        pricePerKgPaise: json['farmer_price_per_kg_paise'] as int,
        totalValuePaise: json['farmer_total_value_paise'] as int,
        status: json['status'] as String,
      );
}

class BidOffer {
  BidOffer({
    required this.id,
    required this.pricePerKgPaise,
    required this.totalOfferPaise,
    required this.serverSequence,
    required this.status,
  });

  final String id;
  final int pricePerKgPaise;
  final int totalOfferPaise;
  final int serverSequence;
  final String status;

  factory BidOffer.fromJson(Map<String, dynamic> json) => BidOffer(
        id: json['bid_id'] as String,
        pricePerKgPaise: json['price_per_kg_paise'] as int,
        totalOfferPaise: json['total_offer_paise'] as int,
        serverSequence: json['server_sequence'] as int,
        status: json['status'] as String,
      );
}
