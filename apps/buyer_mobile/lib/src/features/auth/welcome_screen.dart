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
              Text('PashuSetu Buyer', style: Theme.of(context).textTheme.headlineMedium),
              const Text('Find and buy verified goats and lots'),
              const Spacer(),
              FilledButton(
                onPressed: () => context.go('/register'),
                child: const Text('New Buyer Registration'),
              ),
              const SizedBox(height: 10),
              OutlinedButton(
                onPressed: () => context.go('/login'),
                child: const Text('Existing Buyer Login'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
