import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../shared/money.dart';
import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
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
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);
    return Scaffold(
      appBar: AppBar(title: Text(t('price_listing_rules'))),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          DropdownButtonFormField<String>(
            initialValue: targetType,
            items: [
              DropdownMenuItem(value: 'GOAT', child: Text(t('individual_goat'))),
              DropdownMenuItem(value: 'LOT', child: Text(t('multiple_goats_lot'))),
            ],
            onChanged: (v) => setState(() => targetType = v ?? 'LOT'),
          ),
          const SizedBox(height: 10),
          TextField(controller: targetId, decoration: InputDecoration(labelText: t('goat_id_lot_id'))),
          const SizedBox(height: 10),
          TextField(
            controller: weight,
            enabled: false,
            decoration: InputDecoration(
              labelText: t('verified_weight'),
              helperText: t('review_weighment_note'),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              title: Text(t('market_recommendation')),
              subtitle: Text(
                recommendationPaise == null
                    ? t('no_recommendation')
                    : '${formatPaise(recommendationPaise!)}/kg',
              ),
              trailing: recommendationPaise == null
                  ? null
                  : TextButton(
                      onPressed: () => setState(
                        () => price.text = (recommendationPaise! / 100).toStringAsFixed(0),
                      ),
                      child: Text(t('use')),
                    ),
            ),
          ),
          TextField(
            controller: price,
            keyboardType: TextInputType.number,
            onChanged: (_) => setState(() {}),
            decoration: InputDecoration(labelText: t('your_price')),
          ),
          const SizedBox(height: 12),
          Card(
            child: ListTile(
              title: Text(t('estimated_listing_value')),
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
            title: Text(t('ack_verified_weighment')),
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
            child: Text(t('publish_verified_listing')),
          ),
        ],
      ),
    );
  }
}
