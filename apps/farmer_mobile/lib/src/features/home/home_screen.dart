import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../shared/app_card.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.go('/profile'),
          icon: const CircleAvatar(child: Icon(Icons.person)),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(t('namaste')),
            Text(t('farmer_dashboard'), style: const TextStyle(fontSize: 12)),
          ],
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Row(
            children: [
              Expanded(child: _Kpi(value: '0', label: t('live_listings'))),
              const SizedBox(width: 8),
              Expanded(child: _Kpi(value: '0', label: t('offers'))),
              const SizedBox(width: 8),
              Expanded(child: _Kpi(value: '₹0', label: t('settled'))),
            ],
          ),
          const SizedBox(height: 16),
          AppCard(
            onTap: () => context.go('/livestock/new'),
            child: ListTile(
              leading: const Icon(Icons.add_circle_outline),
              title: Text(t('add_goat_lot')),
              subtitle: Text(t('add_goat_lot_desc')),
            ),
          ),
          AppCard(
            onTap: () => context.go('/listings'),
            child: ListTile(
              leading: const Icon(Icons.inventory_2_outlined),
              title: Text(t('your_listings')),
              subtitle: Text(t('your_listings_desc')),
            ),
          ),
          AppCard(
            onTap: () => context.go('/listing/create'),
            child: ListTile(
              leading: const Icon(Icons.sell_outlined),
              title: Text(t('create_verified_listing')),
              subtitle: Text(t('create_verified_listing_desc')),
            ),
          ),
        ],
      ),
    );
  }
}

class _Kpi extends StatelessWidget {
  const _Kpi({required this.value, required this.label});
  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 14),
        child: Column(children: [
          Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          Text(label, style: const TextStyle(fontSize: 9), textAlign: TextAlign.center),
        ]),
      ),
    );
  }
}
