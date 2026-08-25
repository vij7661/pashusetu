import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Buyer Profile')),
      body: FutureBuilder<Map<String,dynamic>>(
        future: ref.read(buyerRepositoryProvider).me(),
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) return Center(child: Text(snapshot.error.toString()));
          final p = snapshot.data!;
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const CircleAvatar(radius: 36, child: Icon(Icons.storefront)),
              const SizedBox(height: 14),
              ListTile(title: const Text('Buyer ID'), subtitle: Text(p['buyer_id'].toString())),
              ListTile(title: const Text('Business'), subtitle: Text(p['business_name'].toString())),
              ListTile(title: const Text('Buyer type'), subtitle: Text(p['buyer_type'].toString())),
              ListTile(title: const Text('KYC'), subtitle: Text(p['kyc_status'].toString())),
              ListTile(title: const Text('Business verified'), subtitle: Text(p['business_verified'].toString())),
            ],
          );
        },
      ),
    );
  }
}
