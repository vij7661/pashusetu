class WeighmentStrings {
  static const values = <String, Map<String, String>>{
    'en': {
      'reject_weight': 'Reject weight',
      'reweigh_required': 'Weight rejected. The Operator must start a reweigh on the livestock scale.',
    },
    'te': {
      'reject_weight': 'బరువును తిరస్కరించండి',
      'reweigh_required': 'బరువు తిరస్కరించబడింది. ఆపరేటర్ పశువుల స్కేల్‌పై మళ్లీ బరువు కొలత ప్రారంభించాలి.',
    },
    'hi': {
      'reject_weight': 'वजन अस्वीकार करें',
      'reweigh_required': 'वजन अस्वीकार किया गया। ऑपरेटर को पशु तराजू पर दोबारा वजन शुरू करना होगा।',
    },
    'mr': {
      'reject_weight': 'वजन नाकारा',
      'reweigh_required': 'वजन नाकारले आहे. ऑपरेटरने पशुधन काट्यावर पुन्हा वजन सुरू करणे आवश्यक आहे.',
    },
    'ta': {
      'reject_weight': 'எடையை நிராகரிக்கவும்',
      'reweigh_required': 'எடை நிராகரிக்கப்பட்டது. ஆபரேட்டர் கால்நடை தராசில் மறுஎடையை தொடங்க வேண்டும்.',
    },
    'ml': {
      'reject_weight': 'ഭാരം നിരസിക്കുക',
      'reweigh_required': 'ഭാരം നിരസിച്ചു. ഓപ്പറേറ്റർ കന്നുകാലി ത്രാസിൽ വീണ്ടും തൂക്കൽ ആരംഭിക്കണം.',
    },
  };

  static String tr(String language, String key) =>
      values[language]?[key] ?? values['en']?[key] ?? key;
}
