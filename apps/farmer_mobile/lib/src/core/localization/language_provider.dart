import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LanguageController extends StateNotifier<String> {
  LanguageController() : super('en') {
    initialized = _load();
  }

  late final Future<void> initialized;

  static const _key = 'farmer_language';

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(_key);
    if (saved != null && AppLanguage.supported.contains(saved)) {
      state = saved;
    }
  }

  Future<void> setLanguage(String language) async {
    if (!AppLanguage.supported.contains(language)) return;
    state = language;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, language);
  }

  Future<bool> hasPersistedLanguage() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(_key);
    return saved != null && AppLanguage.supported.contains(saved);
  }
}

class AppLanguage {
  static const supported = {'te', 'hi', 'en', 'mr', 'ta', 'ml'};
}

final languageProvider = StateNotifierProvider<LanguageController, String>(
  (ref) => LanguageController(),
);
