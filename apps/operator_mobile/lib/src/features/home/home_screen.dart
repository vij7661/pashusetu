import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Centre Dashboard'),
            Text('Mandal Centre CHY-02', style: TextStyle(fontSize: 12)),
          ],
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Card(
            child: ListTile(
              leading: Icon(Icons.scale),
              title: Text('Scale A-114'),
              subtitle: Text('Connected · Calibration valid'),
              trailing: Icon(Icons.check_circle, color: Colors.green),
            ),
          ),
          const Card(
            child: ListTile(
              leading: Icon(Icons.print),
              title: Text('QR Printer PR-03'),
              subtitle: Text('Ready'),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.person_search),
              title: const Text('Start Farmer Verification'),
              subtitle: const Text('Lookup farmer, goat or lot and begin weighment.'),
              onTap: () => context.go('/lookup'),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.local_shipping),
              title: const Text('Pickup Verification'),
              onTap: () => context.go('/pickup'),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.warning_amber),
              title: const Text('Controlled Reweigh'),
              subtitle: const Text('Restricted dispute workflow.'),
              onTap: () => context.go('/reweigh'),
            ),
          ),
        ],
      ),
    );
  }
}
