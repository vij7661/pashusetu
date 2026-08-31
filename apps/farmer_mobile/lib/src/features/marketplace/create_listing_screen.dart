import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../shared/money.dart';
import '../providers.dart';

class CreateListingScreen extends ConsumerStatefulWidget {
  const CreateListingScreen({super.key});

  @override
  ConsumerState<CreateListingScreen> createState() => _CreateListingScreenState();
}

class _CreateListingScreenState extends ConsumerState<CreateListingScreen> {
  final targetId = TextEditingController();
  final price = TextEditingController(text: '400');
  String targetType = 'LOT';
  double? verifiedWeightKg;
  int? recommendationPaise;
  bool acknowledged = false;
  bool loadingEligibility = false;
  String? result;

  int get totalPaise {
    final weight = verifiedWeightKg ?? 0;
    final pricePerKg = double.tryParse(price.text) ?? 0;
    return (weight * pricePerKg * 100).round();
  }

  @override
  void dispose() {
    targetId.dispose();
    price.dispose();
    super.dispose();
  }

  Future<void> loadRecommendation() async {
    try {
      final rows = await ref
          .read(marketplaceRepositoryProvider)
          .recommendations('HYDERABAD');
      if (rows.isNotEmpty && mounted) {
        final value = rows.first['price_per_kg_paise'] as int;
        setState(() => recommendationPaise = value);
      }
    } catch (e) {
      if (mounted) setState(() => result = e.toString());
    }
  }

  Future<void> loadVerifiedWeight() async {
    final code = targetId.text.trim();
    if (code.isEmpty) return;
    setState(() {
      loadingEligibility = true;
      result = null;
      acknowledged = false;
      verifiedWeightKg = null;
    });
    try {
      final eligibility = await ref
          .read(marketplaceRepositoryProvider)
          .listingEligibility(targetType: targetType, targetId: code);
      if (!mounted) return;
      setState(() {
        verifiedWeightKg =
            double.parse(eligibility['verified_weight_kg'].toString());
      });
    } catch (e) {
      if (mounted) setState(() => result = e.toString());
    } finally {
      if (mounted) setState(() => loadingEligibility = false);
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
    final weightText = verifiedWeightKg == null
        ? '-'
        : verifiedWeightKg!.toStringAsFixed(3).replaceFirst(RegExp(r'\.0+$'), '');

    return Scaffold(
      appBar: AppBar(title: Text(t('price_listing_rules'))),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          DropdownButtonFormField<String>(
            initialValue: targetType,
            items: [
              DropdownMenuItem(
                value: 'GOAT',
                child: Text(t('individual_goat')),
              ),
              DropdownMenuItem(
                value: 'LOT',
                child: Text(t('multiple_goats_lot')),
              ),
            ],
            onChanged: (v) => setState(() {
              targetType = v ?? 'LOT';
              verifiedWeightKg = null;
              acknowledged = false;
            }),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: targetId,
            onChanged: (_) => setState(() {
              verifiedWeightKg = null;
              acknowledged = false;
            }),
            decoration: InputDecoration(labelText: t('goat_id_lot_id')),
          ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            onPressed: loadingEligibility || targetId.text.trim().isEmpty
                ? null
                : loadVerifiedWeight,
            icon: loadingEligibility
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.scale_outlined),
            label: Text(t('verified_weight')),
          ),
          const SizedBox(height: 10),
          Card(
            child: ListTile(
              title: Text(t('verified_weight')),
              subtitle: Text(t('review_weighment_note')),
              trailing: Text(
                verifiedWeightKg == null ? '-' : '$weightText kg',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
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
                        () => price.text =
                            (recommendationPaise! / 100).toStringAsFixed(0),
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
              subtitle: Text(
                verifiedWeightKg == null
                    ? t('review_weighment_note')
                    : '$weightText kg × ₹${price.text}/kg',
              ),
              trailing: Text(
                verifiedWeightKg == null ? '-' : formatPaise(totalPaise),
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
            ),
          ),
          CheckboxListTile(
            value: acknowledged,
            onChanged: verifiedWeightKg == null
                ? null
                : (v) => setState(() => acknowledged = v ?? false),
            title: Text(t('ack_verified_weighment')),
          ),
          if (result != null) Text(result!),
          FilledButton(
            onPressed: !acknowledged || verifiedWeightKg == null
                ? null
                : () async {
                    try {
                      final listing = await ref
                          .read(marketplaceRepositoryProvider)
                          .createListing(
                            targetType: targetType,
                            targetId: targetId.text.trim(),
                            pricePerKgPaise:
                                ((double.tryParse(price.text) ?? 0) * 100)
                                    .round(),
                            opensAt: DateTime.now(),
                            closesAt:
                                DateTime.now().add(const Duration(hours: 8)),
                          );
                      if (!mounted) return;
                      setState(() {
                        result =
                            'Published ${listing.id} · ${listing.verifiedWeightKg} kg';
                      });
                    } catch (e) {
                      if (mounted) setState(() => result = e.toString());
                    }
                  },
            child: Text(t('publish_verified_listing')),
          ),
        ],
      ),
    );
  }
}
