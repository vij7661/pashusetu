import 'package:flutter/material.dart';

ThemeData buildTheme() {
  const green = Color(0xFF2F5233);
  const gold = Color(0xFFE8A430);
  const background = Color(0xFFEEF2E4);

  return ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: green,
      primary: green,
      secondary: gold,
      surface: const Color(0xFFFBFAF3),
    ),
    scaffoldBackgroundColor: background,
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
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
    ),
  );
}
