import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/login_screen.dart';
import '../features/home/home_screen.dart';
import '../features/verification/lookup_screen.dart';
import '../features/weighment/live_weighment_screen.dart';
import '../features/weighment/video_screen.dart';
import '../features/weighment/farmer_review_screen.dart';
import '../features/weighment/handoff_screen.dart';
import '../features/logistics/pickup_screen.dart';
import '../features/weighment/dispute_reweigh_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
      GoRoute(path: '/lookup', builder: (_, __) => const LookupScreen()),
      GoRoute(
        path: '/weigh',
        builder: (_, state) => LiveWeighmentScreen(
          targetType: state.uri.queryParameters['type'] ?? 'LOT',
          targetId: state.uri.queryParameters['target'] ?? '',
        ),
      ),
      GoRoute(
        path: '/weighment/:id/video',
        builder: (_, state) => VideoScreen(weighmentId: state.pathParameters['id']!),
      ),
      GoRoute(
        path: '/weighment/:id/review',
        builder: (_, state) => FarmerReviewScreen(weighmentId: state.pathParameters['id']!),
      ),
      GoRoute(
        path: '/weighment/:id/handoff',
        builder: (_, state) => HandoffScreen(weighmentId: state.pathParameters['id']!),
      ),
      GoRoute(path: '/pickup', builder: (_, __) => const PickupScreen()),
      GoRoute(path: '/reweigh', builder: (_, __) => const DisputeReweighScreen()),
    ],
  );
});
