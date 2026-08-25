import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api/api_client.dart';
import 'api/token_store.dart';

final tokenStoreProvider = Provider((ref) => TokenStore());
final apiClientProvider = Provider((ref) => ApiClient(ref.watch(tokenStoreProvider)));
