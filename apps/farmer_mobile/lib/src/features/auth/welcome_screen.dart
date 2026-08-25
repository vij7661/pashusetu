import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              const Spacer(),
              const Text('🐐', style: TextStyle(fontSize: 64)),
              const SizedBox(height: 12),
              Text('PashuSetu', style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 6),
              const Text('Verified goat trade for farmers'),
              const Spacer(),
              FilledButton(
                onPressed: () => context.go('/register'),
                child: const Text('New Farmer Registration'),
              ),
              const SizedBox(height: 10),
              OutlinedButton(
                onPressed: () => context.go('/login'),
                child: const Text('Existing Customer Login'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
