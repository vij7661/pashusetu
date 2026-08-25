import 'package:flutter_test/flutter_test.dart';
import 'package:pashusetu_operator/src/features/scale/scale_adapter.dart';

void main() {
  test('simulated scale eventually returns stable 50kg net', () async {
    final scale = SimulatedScaleAdapter();
    await scale.connect();
    final samples = await scale.samples().toList();
    expect(samples.last.stable, true);
    expect(samples.last.netKg, 50.0);
    await scale.disconnect();
  });
}
