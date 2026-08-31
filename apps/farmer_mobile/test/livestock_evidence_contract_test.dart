import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_farmer/src/features/livestock/livestock_models.dart';

void main() {
  test('parses a valid evidence upload contract', () {
    final contract = EvidenceUploadContract.fromJson({
      'evidence_id': 'evidence-1',
      'storage_key': 'livestock/goat/1/photo.jpg',
      'upload_method': 'PUT',
      'upload_url': 'https://uploads.example.test/object',
      'expires_in_seconds': 900,
    });

    expect(contract.evidenceId, 'evidence-1');
    expect(contract.uploadMethod, 'PUT');
    expect(contract.expiresInSeconds, 900);
  });

  test('rejects unsupported upload methods', () {
    expect(
      () => EvidenceUploadContract.fromJson({
        'evidence_id': 'evidence-1',
        'storage_key': 'livestock/goat/1/photo.jpg',
        'upload_method': 'POST',
        'upload_url': 'https://uploads.example.test/object',
        'expires_in_seconds': 900,
      }),
      throwsFormatException,
    );
  });

  test('rejects non-positive expiry', () {
    expect(
      () => EvidenceUploadContract.fromJson({
        'evidence_id': 'evidence-1',
        'storage_key': 'livestock/goat/1/photo.jpg',
        'upload_method': 'PUT',
        'upload_url': 'https://uploads.example.test/object',
        'expires_in_seconds': 0,
      }),
      throwsFormatException,
    );
  });
}
