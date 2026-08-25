import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/providers.dart';
import 'auth/auth_repository.dart';
import 'weighment/weighment_repository.dart';
import 'logistics/logistics_repository.dart';
import 'scale/scale_adapter.dart';

final authRepositoryProvider = Provider((ref) => AuthRepository(
      ref.watch(apiClientProvider),
      ref.watch(tokenStoreProvider),
    ));

final weighmentRepositoryProvider =
    Provider((ref) => WeighmentRepository(ref.watch(apiClientProvider)));

final logisticsRepositoryProvider =
    Provider((ref) => LogisticsRepository(ref.watch(apiClientProvider)));

final scaleAdapterProvider = Provider<ScaleAdapter>((ref) => SimulatedScaleAdapter());
