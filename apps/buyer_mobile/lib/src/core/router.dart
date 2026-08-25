import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/welcome_screen.dart';
import '../features/auth/login_screen.dart';
import '../features/buyer/register_screen.dart';
import '../features/home/home_screen.dart';
import '../features/buyer/profile_screen.dart';
import '../features/marketplace/listing_screen.dart';
import '../features/marketplace/active_bid_screen.dart';
import '../features/transaction/agreement_screen.dart';
import '../features/transaction/payment_screen.dart';
import '../features/transaction/delivery_screen.dart';
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
      GoRoute(
        path: '/listing/:listingId',
        builder: (_, state) => ListingScreen(listingId: state.pathParameters['listingId']!),
      ),
      GoRoute(
        path: '/listing/:listingId/bids',
        builder: (_, state) => ActiveBidScreen(listingId: state.pathParameters['listingId']!),
      ),
      GoRoute(
        path: '/transaction/:transactionId/agreement',
        builder: (_, state) => AgreementScreen(transactionId: state.pathParameters['transactionId']!),
      ),
      GoRoute(
        path: '/transaction/:transactionId/payment',
        builder: (_, state) => PaymentScreen(transactionId: state.pathParameters['transactionId']!),
      ),
      GoRoute(
        path: '/transaction/:transactionId/delivery',
        builder: (_, state) => DeliveryScreen(transactionId: state.pathParameters['transactionId']!),
      ),
      GoRoute(
        path: '/transaction/:transactionId/dispute',
        builder: (_, state) => DisputeScreen(transactionId: state.pathParameters['transactionId']!),
      ),
      GoRoute(
        path: '/transaction/:transactionId/settlement',
        builder: (_, state) => SettlementScreen(transactionId: state.pathParameters['transactionId']!),
      ),
    ],
  );
});
