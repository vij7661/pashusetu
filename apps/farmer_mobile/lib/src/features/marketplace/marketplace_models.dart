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
