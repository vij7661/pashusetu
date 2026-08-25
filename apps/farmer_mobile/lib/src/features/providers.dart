import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/providers.dart';
import 'identity/identity_repository.dart';
import 'livestock/livestock_repository.dart';
import 'marketplace/marketplace_repository.dart';
import 'transaction/transaction_repository.dart';
import 'disputes/dispute_repository.dart';
import 'weighment/weighment_repository.dart';
import 'evidence/evidence_service.dart';

final identityRepositoryProvider = Provider(
  (ref) => IdentityRepository(ref.watch(apiClientProvider)),
);
final livestockRepositoryProvider = Provider(
  (ref) => LivestockRepository(ref.watch(apiClientProvider)),
);
final marketplaceRepositoryProvider = Provider(
  (ref) => MarketplaceRepository(ref.watch(apiClientProvider)),
);
final transactionRepositoryProvider = Provider(
  (ref) => TransactionRepository(ref.watch(apiClientProvider)),
);
final disputeRepositoryProvider = Provider(
  (ref) => DisputeRepository(ref.watch(apiClientProvider)),
);

final weighmentRepositoryProvider = Provider(
  (ref) => WeighmentRepository(ref.watch(apiClientProvider)),
);
final evidenceServiceProvider = Provider(
  (ref) => EvidenceService(ref.watch(apiClientProvider)),
);
