import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/app_strings.dart';
import '../../core/localization/language_provider.dart';
import '../../shared/numeric_validation.dart';
import '../auth/auth_error_message.dart';
import '../providers.dart';

class CreateLivestockScreen extends ConsumerStatefulWidget {
  const CreateLivestockScreen({super.key});

  @override
  ConsumerState<CreateLivestockScreen> createState() =>
      _CreateLivestockScreenState();
}

class _CreateLivestockScreenState extends ConsumerState<CreateLivestockScreen> {
  bool lot = false;
  final breed = TextEditingController();
  final quantity = TextEditingController();
  String sex = 'MALE';
  bool busy = false;
  String? result;

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
            onSelectionChanged: (v) => setState(() => lot = v.first),
          ),
          const SizedBox(height: 16),
          TextField(
              controller: breed,
              decoration: InputDecoration(labelText: t('breed'))),
          const SizedBox(height: 10),
          if (lot)
            TextField(
              controller: quantity,
              keyboardType: TextInputType.number,
              inputFormatters: const [RejectingDigitsFormatter(maxLength: 3)],
              decoration: InputDecoration(labelText: t('quantity')),
            )
          else
            DropdownButtonFormField<String>(
              initialValue: sex,
              items: [
                DropdownMenuItem(value: 'MALE', child: Text(t('male'))),
                DropdownMenuItem(value: 'FEMALE', child: Text(t('female'))),
                DropdownMenuItem(value: 'UNKNOWN', child: Text(t('unknown'))),
              ],
              onChanged: (v) => setState(() => sex = v ?? 'MALE'),
            ),
          const Spacer(),
          if (result != null) Text(result!),
          FilledButton(
            onPressed: busy
                ? null
                : () async {
                    if (busy) return;
                    setState(() => busy = true);
                    try {
                      if (lot) {
                        if (!isValidLotQuantity(quantity.text)) {
                          setState(() => result = t('invalid_lot_quantity'));
                          return;
                        }
                        final x = await ref
                            .read(livestockRepositoryProvider)
                            .createLot(
                              quantity: int.parse(quantity.text),
                              breedSummary: breed.text.trim(),
                            );
                        setState(() => result = 'Lot ${x.id}');
                      } else {
                        final x = await ref
                            .read(livestockRepositoryProvider)
                            .createGoat(
                              breed: breed.text.trim(),
                              sex: sex,
                            );
                        if (!context.mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('${t('goat_added_success')} ${x.id}'),
                          ),
                        );
                        context.go('/home');
                      }
                    } catch (e) {
                      setState(() => result = authErrorMessage(e, language));
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
