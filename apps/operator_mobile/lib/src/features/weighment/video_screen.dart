import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';

class VideoScreen extends StatefulWidget {
  const VideoScreen({super.key, required this.weighmentId});
  final String weighmentId;

  @override
  State<VideoScreen> createState() => _VideoScreenState();
}

class _VideoScreenState extends State<VideoScreen> {
  final picker = ImagePicker();
  XFile? video;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Verification Video')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          const Card(
            child: ListTile(
              title: Text('Required evidence'),
              subtitle: Text(
                'Goat/Lot ID · scale/app reading · operator · Mandal Centre context',
              ),
            ),
          ),
          if (video != null)
            ListTile(
              leading: const Icon(Icons.videocam),
              title: Text(video!.name),
              subtitle: const Text('Captured locally'),
            ),
          const Spacer(),
          OutlinedButton(
            onPressed: () async {
              final x = await picker.pickVideo(source: ImageSource.camera);
              if (x != null) setState(() => video = x);
            },
            child: const Text('Capture Verification Video'),
          ),
          const SizedBox(height: 10),
          FilledButton(
            onPressed: video == null
                ? null
                : () => context.go('/weighment/${widget.weighmentId}/review'),
            child: const Text('Continue to Farmer Review'),
          ),
        ]),
      ),
    );
  }
}
