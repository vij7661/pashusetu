import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/money.dart';
import '../providers.dart';

class PaymentScreen extends ConsumerStatefulWidget {
  const PaymentScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  ConsumerState<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends ConsumerState<PaymentScreen> {
  Map<String,dynamic>? result;
  String? error;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Secure Buyer Funds')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          const Text(
            'The current backend uses a simulated secured-funds provider. '
            'A real payment/escrow-like provider must be selected before pilot.',
          ),
          if (result != null)
            Card(
              child: ListTile(
                title: Text(formatPaise(result!['amount_paise'] as int)),
                subtitle: Text('Status ${result!['status']}'),
              ),
            ),
          if (error != null) Text(error!, style: const TextStyle(color: Colors.red)),
          const Spacer(),
          FilledButton(
            onPressed: () async {
              try {
                final x = await ref.read(transactionRepositoryProvider).secureFunds(widget.transactionId);
                setState(() => result = x);
              } catch (e) {
                setState(() => error = e.toString());
              }
            },
            child: const Text('Secure Funds'),
          ),
        ]),
      ),
    );
  }
}
