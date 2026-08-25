import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/money.dart';
import '../providers.dart';

class CreateListingScreen extends ConsumerStatefulWidget {
  const CreateListingScreen({super.key});

  @override
  ConsumerState<CreateListingScreen> createState() => _CreateListingScreenState();
}

class _CreateListingScreenState extends ConsumerState<CreateListingScreen> {
  final targetId = TextEditingController();
  final weight = TextEditingController(text: '50');
  final price = TextEditingController(text: '400');
  String targetType = 'LOT';
  int? recommendationPaise;
  bool acknowledged = false;
  String? result;

  int get totalPaise {
    final w = double.tryParse(weight.text) ?? 0;
    final p = double.tryParse(price.text) ?? 0;
    return (w * p * 100).round();
  }

  Future<void> loadRecommendation() async {
    try {
      final rows = await ref.read(marketplaceRepositoryProvider).recommendations('HYDERABAD');
      if (rows.isNotEmpty) {
        final value = rows.first['price_per_kg_paise'] as int;
        setState(() => recommendationPaise = value);
      }
    } catch (e) {
      setState(() => result = e.toString());
    }
  }

  @override
  void initState() {
    super.initState();
    Future.microtask(loadRecommendation);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Price & Listing Rules')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          DropdownButtonFormField<String>(
            initialValue: targetType,
            items: const [
              DropdownMenuItem(value: 'GOAT', child: Text('Individual Goat')),
              DropdownMenuItem(value: 'LOT', child: Text('Lot')),
            ],
            onChanged: (v) => setState(() => targetType = v ?? 'LOT'),
          ),
          const SizedBox(height: 10),
          TextField(controller: targetId, decoration: const InputDecoration(labelText: 'Goat ID / Lot ID')),
          const SizedBox(height: 10),
          TextField(
            controller: weight,
            enabled: false,
            decoration: const InputDecoration(
              labelText: 'Verified weight (demo display)',
              helperText: 'Production value comes from the verified backend weighment.',
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              title: const Text('Average market price recommendation'),
              subtitle: Text(
                recommendationPaise == null
                    ? 'No recommendation available'
                    : '${formatPaise(recommendationPaise!)}/kg',
              ),
              trailing: recommendationPaise == null
                  ? null
                  : TextButton(
                      onPressed: () => setState(
                        () => price.text = (recommendationPaise! / 100).toStringAsFixed(0),
                      ),
                      child: const Text('Use'),
                    ),
            ),
          ),
          TextField(
            controller: price,
            keyboardType: TextInputType.number,
            onChanged: (_) => setState(() {}),
            decoration: const InputDecoration(labelText: 'Your price ₹ / kg'),
          ),
          const SizedBox(height: 12),
          Card(
            child: ListTile(
              title: const Text('Estimated listing value'),
              subtitle: Text('${weight.text} kg × ₹${price.text}/kg'),
              trailing: Text(
                formatPaise(totalPaise),
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
              ),
            ),
          ),
          CheckboxListTile(
            value: acknowledged,
            onChanged: (v) => setState(() => acknowledged = v ?? false),
            title: const Text('I acknowledge the verified weighment'),
          ),
          if (result != null) Text(result!),
          FilledButton(
            onPressed: !acknowledged || targetId.text.trim().isEmpty
                ? null
                : () async {
                    try {
                      final listing = await ref.read(marketplaceRepositoryProvider).createListing(
                        targetType: targetType,
                        targetId: targetId.text.trim(),
                        pricePerKgPaise: ((double.tryParse(price.text) ?? 0) * 100).round(),
                        opensAt: DateTime.now(),
                        closesAt: DateTime.now().add(const Duration(hours: 8)),
                      );
                      setState(() => result = 'Published ${listing.id}');
                    } catch (e) {
                      setState(() => result = e.toString());
                    }
                  },
            child: const Text('Publish Verified Listing'),
          ),
        ],
      ),
    );
  }
}
