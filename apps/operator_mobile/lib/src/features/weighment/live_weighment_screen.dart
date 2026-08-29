import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers.dart';
import '../scale/scale_adapter.dart';

class LiveWeighmentScreen extends ConsumerStatefulWidget {
  const LiveWeighmentScreen({
    super.key,
    required this.targetType,
    required this.targetId,
  });

  final String targetType;
  final String targetId;

  @override
  ConsumerState<LiveWeighmentScreen> createState() => _LiveWeighmentScreenState();
}

class _LiveWeighmentScreenState extends ConsumerState<LiveWeighmentScreen> {
  String? weighmentId;
  String? readingId;
  ScaleSample? sample;
  String? message;
  bool busy = false;
  StreamSubscription<ScaleSample>? sub;

  @override
  void initState() {
    super.initState();
    Future.microtask(_start);
  }

  Future<void> _start() async {
    setState(() => busy = true);
    try {
      final session = await ref.read(weighmentRepositoryProvider).start(
            targetType: widget.targetType,
            targetId: widget.targetId,
            scaleCode: 'A-114',
          );
      weighmentId = session['weighment_id'] as String;

      final scale = ref.read(scaleAdapterProvider);
      await scale.connect();
      sub = scale.samples().listen((s) async {
        setState(() => sample = s);
        final r = await ref.read(weighmentRepositoryProvider).reading(
              weighmentId: weighmentId!,
              grossKg: s.grossKg,
              tareKg: s.tareKg,
              stable: s.stable,
            );
        readingId = r['reading_id'] as String;
      });
    } catch (e) {
      setState(() => message = e.toString());
    } finally {
      setState(() => busy = false);
    }
  }

  @override
  void dispose() {
    sub?.cancel();
    ref.read(scaleAdapterProvider).disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final s = sample;
    return Scaffold(
      appBar: AppBar(title: const Text('Live Weighment')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(children: [
                const Text('CURRENT NET WEIGHT'),
                Text(
                  s == null ? '--' : '${s.netKg.toStringAsFixed(1)} kg',
                  style: const TextStyle(fontSize: 42, fontWeight: FontWeight.bold),
                ),
                if (s != null)
                  Text(
                    'Gross ${s.grossKg.toStringAsFixed(1)} · '
                    'Tare ${s.tareKg.toStringAsFixed(1)}',
                  ),
              ]),
            ),
          ),
          ListTile(
            leading: Icon(
              s?.stable == true ? Icons.check_circle : Icons.timelapse,
              color: s?.stable == true ? Colors.green : null,
            ),
            title: Text(s?.stable == true ? 'Stable weight' : 'Waiting for stable reading'),
          ),
          if (message != null) Text(message!),
          const Spacer(),
          FilledButton(
            onPressed: busy || s?.stable != true || weighmentId == null || readingId == null
                ? null
                : () async {
                    try {
                      await ref.read(weighmentRepositoryProvider).lock(
                            weighmentId: weighmentId!,
                            readingId: readingId!,
                          );
                      if (!context.mounted) return;
                      context.go('/weighment/$weighmentId/video');
                    } catch (e) {
                      setState(() => message = e.toString());
                    }
                  },
            child: const Text('Lock Stable Weight'),
          ),
        ]),
      ),
    );
  }
}
