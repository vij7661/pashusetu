import 'package:flutter/material.dart';

ThemeData buildTheme() {
  const green = Color(0xFF2F5233);
  const darkGreen = Color(0xFF1E3A22);
  const gold = Color(0xFFE8A430);
  const background = Color(0xFFEEF2E4);

  final scheme = ColorScheme.fromSeed(
    seedColor: green,
    primary: green,
    secondary: gold,
    surface: const Color(0xFFFBFAF3),
    brightness: Brightness.light,
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: background,
    appBarTheme: const AppBarTheme(
      backgroundColor: background,
      foregroundColor: darkGreen,
      centerTitle: false,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: gold,
        foregroundColor: const Color(0xFF3B2606),
        minimumSize: const Size.fromHeight(50),
        textStyle: const TextStyle(fontWeight: FontWeight.w700),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: const Color(0xFFFBFAF3),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: Colors.grey.shade300),
      ),
    ),
  );
}
