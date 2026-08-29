import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/money.dart';
import '../providers.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  final quantity = TextEditingController(text: '3');
  final latitude = TextEditingController(text: '17.3850');
  final longitude = TextEditingController(text: '78.4867');
  Future<List<Map<String, dynamic>>>? results;

  void search() {
    final requested = int.tryParse(quantity.text) ?? 0;
    setState(() {
      results = requested < 3
          ? Future.error('Minimum purchase is 3 goats.')
          : ref.read(marketplaceRepositoryProvider).search(
              requiredQuantity: requested,
              latitude: double.parse(latitude.text),
              longitude: double.parse(longitude.text),
            );
    });
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(
          leading: IconButton(onPressed: () => context.go('/profile'), icon: const Icon(Icons.storefront)),
          title: const Text('Verified Marketplace'),
        ),
        body: Column(children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(children: [
              TextField(controller: quantity, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Goats required (minimum 3)')),
              Row(children: [
                Expanded(child: TextField(controller: latitude, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Search latitude'))),
                const SizedBox(width: 8),
                Expanded(child: TextField(controller: longitude, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Search longitude'))),
                IconButton(onPressed: search, icon: const Icon(Icons.search)),
              ]),
            ]),
          ),
          Expanded(
            child: results == null
                ? const Center(child: Text('Enter quantity and search location to view listings.'))
                : FutureBuilder<List<Map<String, dynamic>>>(
                    future: results,
                    builder: (context, snapshot) {
                      if (snapshot.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
                      if (snapshot.hasError) return Center(child: Text(snapshot.error.toString()));
                      final rows = snapshot.data ?? [];
                      if (rows.isEmpty) return const Center(child: Text('No eligible listings found.'));
                      return ListView.builder(
                        itemCount: rows.length,
                        itemBuilder: (_, index) {
                          final row = rows[index];
                          final id = row['listing_id'].toString();
                          final goats = (row['available_goat_ids'] as List).map((x) => x.toString()).toList();
                          return Card(child: ListTile(
                            title: Text('$id · ${row['available_quantity']} goats'),
                            subtitle: Text('${row['distance_km'] == null ? 'Distance unavailable' : '${row['distance_km']} km away'}\n${row['verified_weight_kg']} kg · ${formatPaise(row['farmer_price_per_kg_paise'] as int)}/kg\nTransport estimate ${row['estimated_transport_paise'] == null ? 'unavailable' : formatPaise(row['estimated_transport_paise'] as int)} · Landed ${row['estimated_landed_cost_paise'] == null ? 'unavailable' : formatPaise(row['estimated_landed_cost_paise'] as int)}'),
                            trailing: FilledButton(
                              onPressed: () => context.go(Uri(path: '/listing/$id', queryParameters: {
                                'quantity': quantity.text,
                                'goats': goats.join(','),
                                'partial': row['partial_bidding_eligible'].toString(),
                              }).toString()),
                              child: const Text('View'),
                            ),
                          ));
                        },
                      );
                    },
                  ),
          ),
        ]),
      );
}
