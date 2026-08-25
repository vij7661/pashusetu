import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/providers.dart';
import 'auth/auth_repository.dart';
import 'buyer/buyer_repository.dart';
import 'marketplace/marketplace_repository.dart';
import 'transaction/transaction_repository.dart';
import 'logistics/logistics_repository.dart';
import 'disputes/dispute_repository.dart';

final authRepositoryProvider = Provider((ref) => AuthRepository(
      ref.watch(apiClientProvider),
      ref.watch(tokenStoreProvider),
    ));
final buyerRepositoryProvider = Provider((ref) => BuyerRepository(ref.watch(apiClientProvider)));
final marketplaceRepositoryProvider =
    Provider((ref) => MarketplaceRepository(ref.watch(apiClientProvider)));
final transactionRepositoryProvider =
    Provider((ref) => TransactionRepository(ref.watch(apiClientProvider)));
final logisticsRepositoryProvider =
    Provider((ref) => LogisticsRepository(ref.watch(apiClientProvider)));
final disputeRepositoryProvider =
    Provider((ref) => DisputeRepository(ref.watch(apiClientProvider)));
