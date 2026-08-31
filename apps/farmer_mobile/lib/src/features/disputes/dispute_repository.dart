import '../../core/api/api_client.dart';
import 'dispute_models.dart';

class DisputeRepository {
  DisputeRepository(this._api);
  final ApiClient _api;

  Future<DisputeView> open({
    required String transactionId,
    required String reason,
    required int disputedAmountPaise,
  }) async {
    final json = await _api.post('/disputes/transactions/$transactionId', body: {
      'reason': reason,
      'disputed_amount_paise': disputedAmountPaise,
    });
    return DisputeView.fromJson(json);
  }

  Future<DisputeEvidenceView> addEvidence({
    required String disputeId,
    required String evidenceType,
    required String evidenceReference,
  }) async {
    final json = await _api.post('/disputes/$disputeId/evidence', body: {
      'evidence_type': evidenceType,
      'evidence_reference': evidenceReference,
    });
    return DisputeEvidenceView.fromJson(json);
  }

  Future<DisputeReweighView> attachReweigh({
    required String disputeId,
    required String weighmentId,
    required String stage,
  }) async {
    final json = await _api.post('/disputes/$disputeId/reweigh', body: {
      'weighment_id': weighmentId,
      'stage': stage,
    });
    return DisputeReweighView.fromJson(json);
  }
}
