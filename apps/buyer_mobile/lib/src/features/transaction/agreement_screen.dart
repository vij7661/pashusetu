import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers.dart';

class AgreementScreen extends ConsumerStatefulWidget {
  const AgreementScreen({super.key, required this.transactionId});
  final String transactionId;

  @override
  ConsumerState<AgreementScreen> createState() => _AgreementScreenState();
}

class _AgreementScreenState extends ConsumerState<AgreementScreen> {
  String? message;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Transaction Agreement')),
      body: FutureBuilder<Map<String,dynamic>>(
        future: ref.read(transactionRepositoryProvider).activeAgreement(widget.transactionId),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) return Center(child: Text(snapshot.error.toString()));
          final a = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              ListTile(title: const Text('Price basis'), subtitle: Text(a['price_basis'].toString())),
              ListTile(title: const Text('Pickup point'), subtitle: Text(a['pickup_point'].toString())),
              ListTile(title: const Text('Final weighing'), subtitle: Text(a['final_weighing_point'].toString())),
              ListTile(title: const Text('Tolerance'), subtitle: Text('${a['tolerance_percent']}%')),
              ListTile(title: const Text('Transport'), subtitle: Text(a['transport_responsibility'].toString())),
              ListTile(title: const Text('Dispute rule'), subtitle: Text(a['dispute_rule'].toString())),
              if (message != null) Text(message!),
              FilledButton(
                onPressed: () async {
                  try {
                    await ref.read(transactionRepositoryProvider).confirmAgreement(
                      widget.transactionId,
                      a['agreement_id'].toString(),
                    );
                    setState(() => message = 'Buyer confirmation recorded.');
                  } catch (e) {
                    setState(() => message = e.toString());
                  }
                },
                child: const Text('Confirm Agreement'),
              ),
            ],
          );
        },
      ),
    );
  }
}
