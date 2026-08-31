import 'dart:io';

Future<void> main() async {
  final projectDir = File.fromUri(Platform.script).parent.parent;

  final create = await Process.run(
    'flutter',
    ['create', '--platforms=android', '--project-name', 'pashusetu_farmer', '.'],
    workingDirectory: projectDir.path,
    runInShell: true,
  );
  stdout.write(create.stdout);
  stderr.write(create.stderr);
  if (create.exitCode != 0) {
    exitCode = create.exitCode;
    return;
  }

  final gradle = File(
    '${projectDir.path}${Platform.pathSeparator}android${Platform.pathSeparator}'
    'app${Platform.pathSeparator}build.gradle.kts',
  );
  var text = await gradle.readAsString();

  if (!text.contains('isCoreLibraryDesugaringEnabled = true')) {
    final compileOptions = RegExp(r'(^\s*compileOptions\s*\{\s*$)', multiLine: true);
    if (!compileOptions.hasMatch(text)) {
      stderr.writeln('Generated Flutter Android compileOptions block not found.');
      exitCode = 2;
      return;
    }
    text = text.replaceFirstMapped(
      compileOptions,
      (match) => '${match.group(1)}\n        isCoreLibraryDesugaringEnabled = true',
    );
  }

  const desugaringDependency =
      'coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")';
  if (!text.contains(desugaringDependency)) {
    text = '$text\n\ndependencies {\n    $desugaringDependency\n}\n';
  }
  await gradle.writeAsString(text);

  final debugManifest = File(
    '${projectDir.path}${Platform.pathSeparator}android${Platform.pathSeparator}'
    'app${Platform.pathSeparator}src${Platform.pathSeparator}debug'
    '${Platform.pathSeparator}AndroidManifest.xml',
  );
  await debugManifest.parent.create(recursive: true);
  await debugManifest.writeAsString('''<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:usesCleartextTraffic="true" />
</manifest>
''');

  stdout.writeln('Farmer Android manual-QA host is ready.');
  stdout.writeln('Cleartext HTTP is enabled only for the debug manifest.');
}
