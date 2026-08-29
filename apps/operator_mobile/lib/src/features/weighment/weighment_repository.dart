import '../../core/api/api_client.dart';

class WeighmentRepository {
  WeighmentRepository(this._api);
  final ApiClient _api;

  Future<Map<String, dynamic>> start({
    required String targetType,
    required String targetId,
    required String scaleCode,
  }) {
    return _api.post('/weighment/sessions', body: {
      'target_type': targetType,
      'target_id': targetId,
      'scale_code': scaleCode,
    });
  }

  Future<Map<String, dynamic>> reading({
    required String weighmentId,
    required double grossKg,
    required double tareKg,
    required bool stable,
  }) {
    return _api.post('/weighment/sessions/$weighmentId/readings', body: {
      'gross_kg': grossKg,
      'tare_kg': tareKg,
      'stable': stable,
    });
  }

  Future<Map<String, dynamic>> lock({
    required String weighmentId,
    required String readingId,
  }) {
    return _api.post('/weighment/sessions/$weighmentId/lock', body: {
      'reading_id': readingId,
    });
  }

  Future<Map<String, dynamic>> attachVideo({
    required String weighmentId,
    required String evidenceId,
  }) {
    return _api.post('/weighment/sessions/$weighmentId/verification-video', body: {
      'video_evidence_id': evidenceId,
    });
  }

  Future<Map<String, dynamic>> createVideoEvidence({
    required String weighmentId,
    required String fileName,
    required String mimeType,
  }) {
    return _api.post('/weighment/sessions/$weighmentId/verification-evidence', body: {
      'file_name': fileName,
      'mime_type': mimeType,
    });
  }

  Future<Map<String, dynamic>> reweigh({
    required String weighmentId,
    required String scaleCode,
  }) {
    return _api.post('/weighment/sessions/$weighmentId/reweigh', body: {
      'scale_code': scaleCode,
    });
  }
}
