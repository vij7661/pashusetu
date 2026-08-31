class Goat {
  Goat({
    required this.id,
    required this.status,
    this.breed,
    this.sex,
    this.ageMonths,
    this.healthNotes,
  });

  final String id;
  final String status;
  final String? breed;
  final String? sex;
  final int? ageMonths;
  final String? healthNotes;

  factory Goat.fromJson(Map<String, dynamic> json) => Goat(
        id: json['goat_id'] as String,
        status: json['status'] as String,
        breed: json['breed'] as String?,
        sex: json['sex'] as String?,
        ageMonths: json['age_months'] as int?,
        healthNotes: json['health_notes'] as String?,
      );
}

class Lot {
  Lot({
    required this.id,
    required this.declaredQuantity,
    required this.linkedGoatIds,
    required this.status,
    this.breedSummary,
  });

  final String id;
  final int declaredQuantity;
  final List<String> linkedGoatIds;
  final String status;
  final String? breedSummary;

  factory Lot.fromJson(Map<String, dynamic> json) => Lot(
        id: json['lot_id'] as String,
        declaredQuantity: json['declared_quantity'] as int,
        linkedGoatIds: (json['linked_goat_ids'] as List<dynamic>? ?? const [])
            .map((e) => e.toString())
            .toList(),
        status: json['status'] as String,
        breedSummary: json['breed_summary'] as String?,
      );
}

class EvidenceUploadContract {
  const EvidenceUploadContract({
    required this.evidenceId,
    required this.storageKey,
    required this.uploadMethod,
    required this.uploadUrl,
    required this.expiresInSeconds,
  });

  final String evidenceId;
  final String storageKey;
  final String uploadMethod;
  final String uploadUrl;
  final int expiresInSeconds;

  factory EvidenceUploadContract.fromJson(Map<String, dynamic> json) {
    String requiredString(String key) {
      final value = json[key];
      if (value is! String || value.isEmpty) {
        throw FormatException('Invalid evidence upload contract field: $key');
      }
      return value;
    }

    final method = requiredString('upload_method');
    if (method != 'PUT') {
      throw FormatException('Unsupported evidence upload method: $method');
    }

    final expires = json['expires_in_seconds'];
    if (expires is! int || expires <= 0) {
      throw const FormatException('Invalid evidence upload expiry.');
    }

    final url = requiredString('upload_url');
    final parsed = Uri.tryParse(url);
    if (parsed == null || !parsed.hasScheme) {
      throw const FormatException('Invalid evidence upload URL.');
    }

    return EvidenceUploadContract(
      evidenceId: requiredString('evidence_id'),
      storageKey: requiredString('storage_key'),
      uploadMethod: method,
      uploadUrl: url,
      expiresInSeconds: expires,
    );
  }
}
