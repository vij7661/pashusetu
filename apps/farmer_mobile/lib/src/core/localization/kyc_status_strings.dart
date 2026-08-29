class KycStatusStrings {
  static const values = <String, Map<String, String>>{
    'en': {
      'pending': 'KYC verification pending',
      'action_required': 'KYC action required',
      'rejected': 'KYC verification rejected',
      'incomplete': 'KYC verification incomplete',
      'transaction_note': 'You can use Home and manage livestock while KYC is incomplete. Transaction actions become available after verification.',
      'available_after_kyc': 'Available after KYC verification',
      'dashboard_state_error': 'Unable to load the current KYC state. Please refresh and try again.',
    },
    'te': {
      'pending': 'KYC ధృవీకరణ పెండింగ్‌లో ఉంది',
      'action_required': 'KYC కోసం చర్య అవసరం',
      'rejected': 'KYC ధృవీకరణ తిరస్కరించబడింది',
      'incomplete': 'KYC ధృవీకరణ పూర్తి కాలేదు',
      'transaction_note': 'KYC పూర్తి కాకపోయినా హోమ్‌ను ఉపయోగించి పశువులను నిర్వహించవచ్చు. ధృవీకరణ పూర్తైన తర్వాత లావాదేవీ చర్యలు అందుబాటులోకి వస్తాయి.',
      'available_after_kyc': 'KYC ధృవీకరణ తర్వాత అందుబాటులో ఉంటుంది',
      'dashboard_state_error': 'ప్రస్తుత KYC స్థితిని లోడ్ చేయలేకపోయాం. రిఫ్రెష్ చేసి మళ్లీ ప్రయత్నించండి.',
    },
    'hi': {
      'pending': 'KYC सत्यापन लंबित है',
      'action_required': 'KYC के लिए कार्रवाई आवश्यक है',
      'rejected': 'KYC सत्यापन अस्वीकृत हुआ',
      'incomplete': 'KYC सत्यापन अधूरा है',
      'transaction_note': 'KYC अधूरा होने पर भी आप होम का उपयोग और पशुधन प्रबंधन कर सकते हैं। सत्यापन के बाद लेनदेन सुविधाएं उपलब्ध होंगी।',
      'available_after_kyc': 'KYC सत्यापन के बाद उपलब्ध',
      'dashboard_state_error': 'वर्तमान KYC स्थिति लोड नहीं हो सकी। कृपया रीफ्रेश करके फिर प्रयास करें।',
    },
    'mr': {
      'pending': 'KYC पडताळणी प्रलंबित आहे',
      'action_required': 'KYC साठी कृती आवश्यक आहे',
      'rejected': 'KYC पडताळणी नाकारली गेली',
      'incomplete': 'KYC पडताळणी अपूर्ण आहे',
      'transaction_note': 'KYC अपूर्ण असतानाही होम वापरता येईल आणि पशुधन व्यवस्थापित करता येईल. पडताळणीनंतर व्यवहार उपलब्ध होतील.',
      'available_after_kyc': 'KYC पडताळणीनंतर उपलब्ध',
      'dashboard_state_error': 'सध्याची KYC स्थिती लोड करता आली नाही. रिफ्रेश करून पुन्हा प्रयत्न करा.',
    },
    'ta': {
      'pending': 'KYC சரிபார்ப்பு நிலுவையில் உள்ளது',
      'action_required': 'KYC க்கு நடவடிக்கை தேவை',
      'rejected': 'KYC சரிபார்ப்பு நிராகரிக்கப்பட்டது',
      'incomplete': 'KYC சரிபார்ப்பு முழுமையில்லை',
      'transaction_note': 'KYC முழுமையில்லாவிட்டாலும் முகப்பு மற்றும் கால்நடை மேலாண்மையை பயன்படுத்தலாம். சரிபார்ப்பு முடிந்த பிறகு பரிவர்த்தனை செயல்கள் கிடைக்கும்.',
      'available_after_kyc': 'KYC சரிபார்ப்புக்குப் பிறகு கிடைக்கும்',
      'dashboard_state_error': 'தற்போதைய KYC நிலையை ஏற்ற முடியவில்லை. புதுப்பித்து மீண்டும் முயற்சிக்கவும்.',
    },
    'ml': {
      'pending': 'KYC സ്ഥിരീകരണം ബാക്കിയുണ്ട്',
      'action_required': 'KYCയ്ക്ക് നടപടി ആവശ്യമാണ്',
      'rejected': 'KYC സ്ഥിരീകരണം നിരസിച്ചു',
      'incomplete': 'KYC സ്ഥിരീകരണം പൂർത്തിയായിട്ടില്ല',
      'transaction_note': 'KYC പൂർത്തിയായിട്ടില്ലെങ്കിലും ഹോം ഉപയോഗിക്കാനും കന്നുകാലികളെ നിയന്ത്രിക്കാനും കഴിയും. സ്ഥിരീകരണത്തിന് ശേഷം ഇടപാട് പ്രവർത്തനങ്ങൾ ലഭ്യമാകും.',
      'available_after_kyc': 'KYC സ്ഥിരീകരണത്തിന് ശേഷം ലഭ്യം',
      'dashboard_state_error': 'നിലവിലെ KYC സ്ഥിതി ലോഡ് ചെയ്യാനായില്ല. പുതുക്കി വീണ്ടും ശ്രമിക്കുക.',
    },
  };

  static String tr(String language, String key) {
    return values[language]?[key] ?? values['en']![key]!;
  }
}
