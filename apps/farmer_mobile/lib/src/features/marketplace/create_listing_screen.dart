import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../shared/money.dart';
import '../providers.dart';

const defaultListingWindow = Duration(hours: 8);

class CreateListingScreen extends ConsumerStatefulWidget {
  const CreateListingScreen({super.key});

  @override
  ConsumerState<CreateListingScreen> createState() => _CreateListingScreenState();
}

class _CreateListingScreenState extends ConsumerState<CreateListingScreen> {
  final targetId = TextEditingController();
  final price = TextEditingController();
  String targetType = 'LOT';
  double? verifiedWeightKg;
  int? recommendationPaise;
  String? recommendationId;
  String? selectedRecommendationId;
  bool acknowledged = false;
  bool loadingContext = false;
  bool publishing = false;
  String? result;

  int get totalPaise {
    final weight = verifiedWeightKg ?? 0;
    final pricePerKg = double.tryParse(price.text) ?? 0;
    return (weight * pricePerKg * 100).round();
  }

  bool get canPublish {
    final pricePerKg = double.tryParse(price.text);
    return !publishing &&
        acknowledged &&
        verifiedWeightKg != null &&
        targetId.text.trim().isNotEmpty &&
        pricePerKg != null &&
        pricePerKg > 0;
  }

  void invalidateContext() {
    setState(() {
      verifiedWeightKg = null;
      recommendationPaise = null;
      recommendationId = null;
      selectedRecommendationId = null;
      acknowledged = false;
      result = null;
    });
  }

  Future<void> loadContext() async {
    if (targetId.text.trim().isEmpty || loadingContext) return;
    setState(() {
      loadingContext = true;
      verifiedWeightKg = null;
      recommendationPaise = null;
      recommendationId = null;
      selectedRecommendationId = null;
      acknowledged = false;
      result = null;
    });
    try {
      final repository = ref.read(marketplaceRepositoryProvider);
      final context = await repository.listingContext(
        targetType: targetType,
        targetId: targetId.text.trim(),
      );
      final weight = double.parse(context['verified_weight_kg'].toString());
      final marketCode = context['market_code'].toString();
      final rows = await repository.recommendations(marketCode);
      if (!mounted) return;
      setState(() {
        verifiedWeightKg = weight;
        if (rows.isNotEmpty) {
          recommendationPaise = rows.first['price_per_kg_paise'] as int;
          recommendationId = rows.first['recommendation_id'].toString();
        }
      });
    } catch (e) {
      if (mounted) setState(() => result = e.toString());
    } finally {
      if (mounted) setState(() => loadingContext = false);
    }
  }

  @override
  void dispose() {
    targetId.dispose();
    price.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);
    final weightLabel = verifiedWeightKg == null
        ? '—'
        : '${verifiedWeightKg!.toStringAsFixed(3)} kg';

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
            onChanged: (v) {
              final value = v ?? 'LOT';
              if (value != targetType) {
                targetType = value;
                invalidateContext();
              }
            },
          ),
          const SizedBox(height: 10),
          TextField(
            controller: targetId,
            onChanged: (_) => invalidateContext(),
            decoration: InputDecoration(labelText: t('goat_id_lot_id')),
          ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            onPressed: loadingContext || targetId.text.trim().isEmpty
                ? null
                : loadContext,
            icon: loadingContext
                ? const SizedBox.square(
                    dimension: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.scale_outlined),
            label: Text(t('verified_weight')),
          ),
          const SizedBox(height: 10),
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: Text(t('verified_weight')),
            subtitle: Text(t('review_weighment_note')),
            trailing: Text(
              weightLabel,
              style: const TextStyle(fontWeight: FontWeight.bold),
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
                      onPressed: () => setState(() {
                        price.text =
                            (recommendationPaise! / 100).toStringAsFixed(0);
                        selectedRecommendationId = recommendationId;
                      }),
                      child: Text(t('use')),
                    ),
            ),
          ),
          TextField(
            controller: price,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            onChanged: (_) => setState(() => selectedRecommendationId = null),
            decoration: InputDecoration(labelText: t('your_price')),
          ),
          const SizedBox(height: 12),
          Card(
            child: ListTile(
              title: Text(t('estimated_listing_value')),
              subtitle: Text(
                verifiedWeightKg == null
                    ? '—'
                    : '$weightLabel × ₹${price.text.isEmpty ? '—' : price.text}/kg',
              ),
              trailing: Text(
                formatPaise(totalPaise),
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
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
            onPressed: canPublish
                ? () async {
                    setState(() {
                      publishing = true;
                      result = null;
                    });
                    try {
                      final listing = await ref
                          .read(marketplaceRepositoryProvider)
                          .createListing(
                            targetType: targetType,
                            targetId: targetId.text.trim(),
                            pricePerKgPaise:
                                (double.parse(price.text) * 100).round(),
                            opensAt: DateTime.now(),
                            closesAt:
                                DateTime.now().add(defaultListingWindow),
                            recommendationId: selectedRecommendationId,
                          );
                      if (mounted) {
                        setState(() => result = 'Published ${listing.id}');
                      }
                    } catch (e) {
                      if (mounted) setState(() => result = e.toString());
                    } finally {
                      if (mounted) setState(() => publishing = false);
                    }
                  }
                : null,
            child: Text(t('publish_verified_listing')),
          ),
        ],
      ),
    );
  }
}
