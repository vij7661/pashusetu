import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers.dart';
import '../../shared/money.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});
  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  double? minWeight;
  double? maxWeight;
  late Future<List<Map<String,dynamic>>> future;

  @override
  void initState() {
    super.initState();
    future = ref.read(marketplaceRepositoryProvider).search();
  }

  void refresh() {
    setState(() {
      future = ref.read(marketplaceRepositoryProvider).search(
        minWeightKg: minWeight,
        maxWeightKg: maxWeight,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.go('/profile'),
          icon: const CircleAvatar(child: Icon(Icons.storefront)),
        ),
        title: const Text('Verified Marketplace'),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(children: [
              Expanded(
                child: TextField(
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Min kg'),
                  onChanged: (v) => minWeight = double.tryParse(v),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextField(
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Max kg'),
                  onChanged: (v) => maxWeight = double.tryParse(v),
                ),
              ),
              IconButton(onPressed: refresh, icon: const Icon(Icons.search)),
            ]),
          ),
          Expanded(
            child: FutureBuilder<List<Map<String,dynamic>>>(
              future: future,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) return Center(child: Text(snapshot.error.toString()));
                final rows = snapshot.data ?? [];
                if (rows.isEmpty) return const Center(child: Text('No verified listings found.'));
                return ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: rows.length,
                  itemBuilder: (_, i) {
                    final x = rows[i];
                    final id = x['listing_id'].toString();
                    return Card(
                      child: ListTile(
                        title: Text('$id · ${x['target_type']}'),
                        subtitle: Text(
                          '${x['verified_weight_kg']} kg\n'
                          '${formatPaise(x['farmer_price_per_kg_paise'] as int)}/kg · '
                          'Total ${formatPaise(x['farmer_total_value_paise'] as int)}',
                        ),
                        trailing: FilledButton(
                          onPressed: () => context.go('/listing/$id'),
                          child: const Text('View'),
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
