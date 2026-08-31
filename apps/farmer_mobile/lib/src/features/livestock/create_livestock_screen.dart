import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../providers.dart';

class CreateLivestockScreen extends ConsumerStatefulWidget {
  const CreateLivestockScreen({super.key});

  @override
  ConsumerState<CreateLivestockScreen> createState() => _CreateLivestockScreenState();
}

class _CreateLivestockScreenState extends ConsumerState<CreateLivestockScreen> {
  bool lot = false;
  final breed = TextEditingController();
  final quantity = TextEditingController();
  String sex = 'UNKNOWN';
  bool busy = false;
  String? result;

  bool get canSubmit {
    if (breed.text.trim().isEmpty) return false;
    if (!lot) return true;
    final parsedQuantity = int.tryParse(quantity.text.trim());
    return parsedQuantity != null && parsedQuantity > 0;
  }

  @override
  void initState() {
    super.initState();
    breed.addListener(_refreshValidation);
    quantity.addListener(_refreshValidation);
  }

  void _refreshValidation() {
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    breed
      ..removeListener(_refreshValidation)
      ..dispose();
    quantity
      ..removeListener(_refreshValidation)
      ..dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    String t(String key) => AppStrings.tr(language, key);

    return Scaffold(
      appBar: AppBar(title: Text(t('add_goat_lot'))),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          SegmentedButton<bool>(
            segments: [
              ButtonSegment(value: false, label: Text(t('individual_goat'))),
              ButtonSegment(value: true, label: Text(t('multiple_goats_lot'))),
            ],
            selected: {lot},
            onSelectionChanged: (v) => setState(() {
              lot = v.first;
              result = null;
            }),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: breed,
            decoration: InputDecoration(labelText: t('breed')),
            textCapitalization: TextCapitalization.words,
          ),
          const SizedBox(height: 10),
          if (lot)
            TextField(
              controller: quantity,
              keyboardType: TextInputType.number,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              decoration: InputDecoration(labelText: t('quantity')),
            )
          else
            DropdownButtonFormField<String>(
              initialValue: sex,
              items: [
                DropdownMenuItem(value: 'UNKNOWN', child: Text(t('unknown'))),
                DropdownMenuItem(value: 'MALE', child: Text(t('male'))),
                DropdownMenuItem(value: 'FEMALE', child: Text(t('female'))),
              ],
              onChanged: (v) => setState(() => sex = v ?? 'UNKNOWN'),
            ),
          const Spacer(),
          if (result != null) Text(result!),
          FilledButton(
            onPressed: busy || !canSubmit
                ? null
                : () async {
                    setState(() => busy = true);
                    try {
                      if (lot) {
                        final parsedQuantity = int.parse(quantity.text.trim());
                        final x = await ref.read(livestockRepositoryProvider).createLot(
                          quantity: parsedQuantity,
                          breedSummary: breed.text.trim(),
                        );
                        if (!mounted) return;
                        setState(() => result = '${t('multiple_goats_lot')}: ${x.id}');
                      } else {
                        final x = await ref.read(livestockRepositoryProvider).createGoat(
                          breed: breed.text.trim(),
                          sex: sex,
                        );
                        if (!mounted) return;
                        setState(() => result = '${t('individual_goat')}: ${x.id}');
                      }
                    } catch (e) {
                      if (!mounted) return;
                      setState(() => result = e.toString());
                    } finally {
                      if (mounted) setState(() => busy = false);
                    }
                  },
            child: Text(lot ? t('create_lot') : t('add_individual_goat')),
          ),
        ]),
      ),
    );
  }
}
