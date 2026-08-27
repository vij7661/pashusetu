import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/money.dart';
import '../providers.dart';

class ListingScreen extends ConsumerStatefulWidget {
  const ListingScreen({
    super.key,
    required this.listingId,
    required this.requestedQuantity,
    required this.availableGoatIds,
    required this.partialEligible,
  });
  final String listingId;
  final int requestedQuantity;
  final List<String> availableGoatIds;
  final bool partialEligible;

  @override
  ConsumerState<ListingScreen> createState() => _ListingScreenState();
}

class _ListingScreenState extends ConsumerState<ListingScreen> {
  final bid = TextEditingController(text: '492');
  String? result;

  @override
  Widget build(BuildContext context) {
    final rupees = double.tryParse(bid.text) ?? 0;
    return Scaffold(
      appBar: AppBar(title: const Text('Verified Listing')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          Card(
            child: ListTile(
              title: Text(widget.listingId),
              subtitle: const Text(
                'Verified listing. Review weight/evidence in the final product before bidding.',
              ),
            ),
          ),
          TextField(
            controller: bid,
            keyboardType: TextInputType.number,
            onChanged: (_) => setState(() {}),
            decoration: const InputDecoration(labelText: 'Your offer ₹ / kg'),
          ),
          const SizedBox(height: 12),
          Card(
            child: ListTile(
              title: const Text('Offer rate'),
              trailing: Text('₹${rupees.toStringAsFixed(0)}/kg'),
            ),
          ),
          if (result != null) Text(result!),
          const Spacer(),
          FilledButton(
            onPressed: () async {
              try {
                final key = 'buyer-${DateTime.now().microsecondsSinceEpoch}';
                final x = await ref.read(marketplaceRepositoryProvider).bid(
                  listingId: widget.listingId,
                  pricePerKgPaise: (rupees * 100).round(),
                  idempotencyKey: key,
                  selectedGoatIds: widget.partialEligible
                      ? widget.availableGoatIds.take(widget.requestedQuantity).toList()
                      : const [],
                  wholeLot: !widget.partialEligible ||
                      widget.requestedQuantity == widget.availableGoatIds.length,
                );
                setState(() {
                  result =
                      'Bid ${x['bid_id']} submitted · ${formatPaise(x['total_offer_paise'] as int)} '
                      '· server sequence #${x['server_sequence']}';
                });
              } catch (e) {
                setState(() => result = e.toString());
              }
            },
            child: const Text('Submit Offer'),
          ),
        ]),
      ),
    );
  }
}
