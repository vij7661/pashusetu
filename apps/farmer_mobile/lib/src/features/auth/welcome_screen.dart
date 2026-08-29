import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/localization/language_provider.dart';

class WelcomeScreen extends ConsumerStatefulWidget {
  const WelcomeScreen({super.key});

  @override
  ConsumerState<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends ConsumerState<WelcomeScreen> {
  bool _preferenceLoaded = false;
  bool _hasLanguagePreference = false;

  @override
  void initState() {
    super.initState();
    Future<void>(() async {
      final controller = ref.read(languageProvider.notifier);
      await controller.initialized;
      final saved = await controller.hasPersistedLanguage();
      if (mounted) {
        setState(() {
          _preferenceLoaded = true;
          _hasLanguagePreference = saved;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final language = ref.watch(languageProvider);
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              const Spacer(),
              const Text('🐐', style: TextStyle(fontSize: 64)),
              const SizedBox(height: 12),
              Text(
                'PashuSetu',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 6),
              const Text('Verified goat trade for farmers'),
              const Spacer(),
              const Text('Choose your language / మీ భాషను ఎంచుకోండి'),
              const SizedBox(height: 10),
              DropdownButtonFormField<String>(
                key: ValueKey(
                  '$_preferenceLoaded-$_hasLanguagePreference-$language',
                ),
                initialValue: _hasLanguagePreference ? language : null,
                decoration: const InputDecoration(labelText: 'Language'),
                items: const [
                  DropdownMenuItem(value: 'en', child: Text('English')),
                  DropdownMenuItem(value: 'te', child: Text('తెలుగు')),
                  DropdownMenuItem(value: 'hi', child: Text('हिन्दी')),
                  DropdownMenuItem(value: 'mr', child: Text('मराठी')),
                  DropdownMenuItem(value: 'ta', child: Text('தமிழ்')),
                  DropdownMenuItem(value: 'ml', child: Text('മലയാളം')),
                ],
                onChanged: (selection) async {
                  if (selection == null) return;
                  await ref
                      .read(languageProvider.notifier)
                      .setLanguage(selection);
                  if (mounted) {
                    setState(() => _hasLanguagePreference = true);
                  }
                },
              ),
              const SizedBox(height: 20),
              FilledButton(
                onPressed: _preferenceLoaded && _hasLanguagePreference
                    ? () => context.go('/register')
                    : null,
                child: const Text('New Farmer Registration'),
              ),
              const SizedBox(height: 10),
              OutlinedButton(
                onPressed: _preferenceLoaded && _hasLanguagePreference
                    ? () => context.go('/login')
                    : null,
                child: const Text('Existing Customer Login'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
