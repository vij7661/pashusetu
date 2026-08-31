import '../../core/api/api_client.dart';
import 'livestock_models.dart';

class LivestockRepository {
  LivestockRepository(this._api);
  final ApiClient _api;

  Future<Goat> createGoat({
    String? breed,
    String? sex,
    int? ageMonths,
    String? healthNotes,
  }) async {
    final json = await _api.post('/livestock/goats', body: {
      'breed': breed,
      'sex': sex,
      'age_months': ageMonths,
      'health_notes': healthNotes,
    });
    return Goat.fromJson(json);
  }

  Future<Lot> createLot({
    required int quantity,
    String? breedSummary,
    String? sexSummary,
    String? ageSummary,
    List<String> goatIds = const [],
  }) async {
    final json = await _api.post('/livestock/lots', body: {
      'declared_quantity': quantity,
      'breed_summary': breedSummary,
      'sex_summary': sexSummary,
      'age_summary': ageSummary,
      'goat_ids': goatIds,
    });
    return Lot.fromJson(json);
  }

  Future<EvidenceUploadContract> createEvidenceContract({
    required String ownerType,
    required String ownerId,
    required String evidenceType,
    required String fileName,
    required String mimeType,
  }) async {
    final json = await _api.post('/livestock/evidence/upload-contract', body: {
      'owner_type': ownerType,
      'owner_id': ownerId,
      'evidence_type': evidenceType,
      'file_name': fileName,
      'mime_type': mimeType,
    });
    return EvidenceUploadContract.fromJson(json);
  }
}
