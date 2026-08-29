import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class LookupScreen extends StatefulWidget {
  const LookupScreen({super.key});

  @override
  State<LookupScreen> createState() => _LookupScreenState();
}

class _LookupScreenState extends State<LookupScreen> {
  final farmer = TextEditingController(text: 'PS-F-DEMO01');
  final target = TextEditingController();
  String targetType = 'LOT';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Farmer / Goat / Lot Lookup')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          TextField(
            controller: farmer,
            decoration: const InputDecoration(labelText: 'Farmer ID / Mobile / QR'),
          ),
          const SizedBox(height: 10),
          DropdownButtonFormField<String>(
            initialValue: targetType,
            items: const [
              DropdownMenuItem(value: 'GOAT', child: Text('Individual Goat')),
              DropdownMenuItem(value: 'LOT', child: Text('Goat Lot')),
            ],
            onChanged: (v) => setState(() => targetType = v ?? 'LOT'),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: target,
            decoration: const InputDecoration(labelText: 'Goat ID / Lot ID'),
          ),
          const Spacer(),
          FilledButton(
            onPressed: target.text.trim().isEmpty
                ? null
                : () => context.go(
                      '/weigh?type=$targetType&target=${target.text.trim()}',
                    ),
            child: const Text('Continue to Weighment'),
          ),
        ]),
      ),
    );
  }
}
