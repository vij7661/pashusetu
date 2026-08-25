import 'dart:io';

import 'package:dio/dio.dart';
import 'package:image_picker/image_picker.dart';

import '../../core/api/api_client.dart';

class EvidenceService {
  EvidenceService(this._api);

  final ApiClient _api;
  final ImagePicker _picker = ImagePicker();
  final Dio _uploadDio = Dio();

  Future<String?> pickAndUploadImage({
    required String ownerType,
    required String ownerId,
    required String evidenceType,
  }) async {
    final file = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 85,
    );
    if (file == null) return null;

    final contract = await _api.post(
      '/livestock/evidence/upload-contract',
      body: {
        'owner_type': ownerType,
        'owner_id': ownerId,
        'evidence_type': evidenceType,
        'file_name': file.name,
        'mime_type': 'image/jpeg',
      },
    );

    final uploadUrl = contract['upload_url'] as String;
    final bytes = await File(file.path).readAsBytes();

    await _uploadDio.put(
      uploadUrl,
      data: Stream.fromIterable([bytes]),
      options: Options(
        headers: {'Content-Type': 'image/jpeg'},
      ),
    );

    return contract['evidence_id'] as String;
  }
}
