class ScaleSample {
  const ScaleSample({
    required this.grossKg,
    required this.tareKg,
    required this.stable,
  });

  final double grossKg;
  final double tareKg;
  final bool stable;

  double get netKg => grossKg - tareKg;
}

abstract class ScaleAdapter {
  Future<void> connect();
  Stream<ScaleSample> samples();
  Future<void> disconnect();
}

class SimulatedScaleAdapter implements ScaleAdapter {
  bool _connected = false;

  @override
  Future<void> connect() async {
    _connected = true;
  }

  @override
  Stream<ScaleSample> samples() async* {
    if (!_connected) throw StateError('Scale not connected');
    yield const ScaleSample(grossKg: 54.2, tareKg: 4.5, stable: false);
    await Future<void>.delayed(const Duration(milliseconds: 500));
    yield const ScaleSample(grossKg: 54.4, tareKg: 4.5, stable: false);
    await Future<void>.delayed(const Duration(milliseconds: 500));
    yield const ScaleSample(grossKg: 54.5, tareKg: 4.5, stable: true);
  }

  @override
  Future<void> disconnect() async {
    _connected = false;
  }
}
