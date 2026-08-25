# Farmer Flutter 3.47 Patch 2

This patch resolves the final `use_build_context_synchronously` analyzer info.

The callback captures the `BuildContext` parameter, so Flutter 3.47 expects that specific
context to be checked after the async gap:

```dart
await c.verifyOtp(...);
if (!context.mounted) return;
if (!ref.read(authControllerProvider).hasError) {
  context.go('/home');
}
```

Run:

```bat
cd apps\farmer_mobile
flutter analyze
flutter test
```
