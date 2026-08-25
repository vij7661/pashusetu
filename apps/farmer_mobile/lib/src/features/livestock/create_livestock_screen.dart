import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers.dart';

class CreateLivestockScreen extends ConsumerStatefulWidget {
  const CreateLivestockScreen({super.key});

  @override
  ConsumerState<CreateLivestockScreen> createState() => _CreateLivestockScreenState();
}

class _CreateLivestockScreenState extends ConsumerState<CreateLivestockScreen> {
  bool lot = false;
  final breed = TextEditingController(text: 'Sirohi');
  final quantity = TextEditingController(text: '1');
  String sex = 'MALE';
  bool busy = false;
  String? result;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add Goat / Create Lot')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          SegmentedButton<bool>(
            segments: const [
              ButtonSegment(value: false, label: Text('Individual Goat')),
              ButtonSegment(value: true, label: Text('Multiple Goats / Lot')),
            ],
            selected: {lot},
            onSelectionChanged: (v) => setState(() => lot = v.first),
          ),
          const SizedBox(height: 16),
          TextField(controller: breed, decoration: const InputDecoration(labelText: 'Breed')),
          const SizedBox(height: 10),
          if (lot)
            TextField(
              controller: quantity,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Quantity'),
            )
          else
            DropdownButtonFormField<String>(
              initialValue: sex,
              items: const [
                DropdownMenuItem(value: 'MALE', child: Text('Male')),
                DropdownMenuItem(value: 'FEMALE', child: Text('Female')),
                DropdownMenuItem(value: 'UNKNOWN', child: Text('Unknown')),
              ],
              onChanged: (v) => setState(() => sex = v ?? 'MALE'),
            ),
          const Spacer(),
          if (result != null) Text(result!),
          FilledButton(
            onPressed: busy
                ? null
                : () async {
                    setState(() => busy = true);
                    try {
                      if (lot) {
                        final x = await ref.read(livestockRepositoryProvider).createLot(
                          quantity: int.parse(quantity.text),
                          breedSummary: breed.text.trim(),
                        );
                        setState(() => result = 'Created Lot ${x.id}');
                      } else {
                        final x = await ref.read(livestockRepositoryProvider).createGoat(
                          breed: breed.text.trim(),
                          sex: sex,
                        );
                        setState(() => result = 'Created Goat ${x.id}');
                      }
                    } catch (e) {
                      setState(() => result = e.toString());
                    } finally {
                      setState(() => busy = false);
                    }
                  },
            child: Text(lot ? 'Create Lot' : 'Add Individual Goat'),
          ),
        ]),
      ),
    );
  }
}
