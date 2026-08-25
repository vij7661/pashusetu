import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/welcome_screen.dart';
import '../features/auth/login_screen.dart';
import '../features/identity/register_screen.dart';
import '../features/home/home_screen.dart';
import '../features/identity/profile_screen.dart';
import '../features/livestock/create_livestock_screen.dart';
import '../features/marketplace/create_listing_screen.dart';
import '../features/marketplace/offers_screen.dart';
import '../features/transaction/transaction_screen.dart';
import '../features/weighment/weighment_ack_screen.dart';
import '../features/marketplace/listing_history_screen.dart';
import '../features/transaction/agreement_screen.dart';
import '../features/transaction/shipment_screen.dart';
import '../features/disputes/dispute_screen.dart';
import '../features/transaction/settlement_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (_, __) => const WelcomeScreen()),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
      GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
      GoRoute(path: '/livestock/new', builder: (_, __) => const CreateLivestockScreen()),
      GoRoute(path: '/listing/create', builder: (_, __) => const CreateListingScreen()),
      GoRoute(path: '/listings', builder: (_, __) => const ListingHistoryScreen()),
      GoRoute(
        path: '/weighment/:weighmentId/ack',
        builder: (_, state) => WeighmentAckScreen(
          weighmentId: state.pathParameters['weighmentId']!,
        ),
      ),
      GoRoute(
        path: '/transaction/:transactionId/agreement',
        builder: (_, state) => AgreementScreen(
          transactionId: state.pathParameters['transactionId']!,
        ),
      ),
      GoRoute(
        path: '/transaction/:transactionId/shipment',
        builder: (_, state) => ShipmentScreen(
          transactionId: state.pathParameters['transactionId']!,
        ),
      ),
      GoRoute(
        path: '/transaction/:transactionId/dispute',
        builder: (_, state) => DisputeScreen(
          transactionId: state.pathParameters['transactionId']!,
        ),
      ),
      GoRoute(
        path: '/transaction/:transactionId/settlement',
        builder: (_, state) => SettlementScreen(
          transactionId: state.pathParameters['transactionId']!,
        ),
      ),
      GoRoute(
        path: '/listing/:listingId/offers',
        builder: (_, state) => OffersScreen(listingId: state.pathParameters['listingId']!),
      ),
      GoRoute(
        path: '/transaction/:transactionId',
        builder: (_, state) => TransactionScreen(
          transactionId: state.pathParameters['transactionId']!,
        ),
      ),
    ],
  );
});
