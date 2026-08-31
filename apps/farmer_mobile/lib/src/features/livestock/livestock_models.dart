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

  factory Goat.fromJson(Map<String, dynamic> json) {
    String requiredString(String key) {
      final value = json[key];
      if (value is! String || value.trim().isEmpty) {
        throw FormatException('Invalid goat field: $key');
      }
      return value.trim();
    }

    final sex = json['sex'];
    if (sex != null && !const {'MALE', 'FEMALE', 'UNKNOWN'}.contains(sex)) {
      throw FormatException('Invalid goat sex: $sex');
    }
    final ageMonths = json['age_months'];
    if (ageMonths != null &&
        (ageMonths is! int || ageMonths < 0 || ageMonths > 300)) {
      throw const FormatException('Invalid goat age_months');
    }

    return Goat(
      id: requiredString('goat_id'),
      status: requiredString('status'),
      breed: json['breed'] as String?,
      sex: sex as String?,
      ageMonths: ageMonths as int?,
      healthNotes: json['health_notes'] as String?,
    );
  }
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

  factory Lot.fromJson(Map<String, dynamic> json) {
    String requiredString(String key) {
      final value = json[key];
      if (value is! String || value.trim().isEmpty) {
        throw FormatException('Invalid lot field: $key');
      }
      return value.trim();
    }

    final declaredQuantity = json['declared_quantity'];
    if (declaredQuantity is! int ||
        declaredQuantity <= 0 ||
        declaredQuantity > 500) {
      throw const FormatException('Invalid lot declared_quantity');
    }

    final rawLinkedIds = json['linked_goat_ids'];
    if (rawLinkedIds is! List) {
      throw const FormatException('Invalid linked_goat_ids');
    }
    final linkedGoatIds = <String>[];
    for (final value in rawLinkedIds) {
      if (value is! String || value.trim().isEmpty) {
        throw const FormatException('Invalid linked goat identifier');
      }
      linkedGoatIds.add(value.trim());
    }
    if (linkedGoatIds.length > declaredQuantity) {
      throw const FormatException('Linked goats exceed declared quantity');
    }

    return Lot(
      id: requiredString('lot_id'),
      declaredQuantity: declaredQuantity,
      linkedGoatIds: linkedGoatIds,
      status: requiredString('status'),
      breedSummary: json['breed_summary'] as String?,
    );
  }
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
