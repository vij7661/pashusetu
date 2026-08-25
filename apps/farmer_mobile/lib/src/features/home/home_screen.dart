import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../shared/app_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.go('/profile'),
          icon: const CircleAvatar(child: Icon(Icons.person)),
        ),
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Namaste'),
            Text('Farmer Dashboard', style: TextStyle(fontSize: 12)),
          ],
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Row(
            children: [
              Expanded(child: _Kpi(value: '0', label: 'LIVE LISTINGS')),
              SizedBox(width: 8),
              Expanded(child: _Kpi(value: '0', label: 'OFFERS')),
              SizedBox(width: 8),
              Expanded(child: _Kpi(value: '₹0', label: 'SETTLED')),
            ],
          ),
          const SizedBox(height: 16),
          AppCard(
            onTap: () => context.go('/livestock/new'),
            child: const ListTile(
              leading: Icon(Icons.add_circle_outline),
              title: Text('Add Goat / Create Lot'),
              subtitle: Text('Add an individual goat or a multi-goat lot.'),
            ),
          ),
          AppCard(
            onTap: () => context.go('/listings'),
            child: const ListTile(
              leading: Icon(Icons.inventory_2_outlined),
              title: Text('Your Listings'),
              subtitle: Text('View live and historical listings.'),
            ),
          ),
          AppCard(
            onTap: () => context.go('/listing/create'),
            child: const ListTile(
              leading: Icon(Icons.sell_outlined),
              title: Text('Create Verified Listing'),
              subtitle: Text('Requires a verified and acknowledged weighment.'),
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
          Text(label, style: const TextStyle(fontSize: 9)),
        ]),
      ),
    );
  }
}
