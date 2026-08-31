class MarketplaceStrings {
  static const values = <String, Map<String, String>>{
    'en': {
      'no_listings': 'No listings yet.',
      'published': 'Published',
      'closed': 'Closed',
      'draft': 'Draft',
      'cancelled': 'Cancelled',
    },
    'te': {
      'no_listings': 'ఇంకా జాబితాలు లేవు.',
      'published': 'ప్రచురించబడింది',
      'closed': 'ముగిసింది',
      'draft': 'ముసాయిదా',
      'cancelled': 'రద్దు చేయబడింది',
    },
    'hi': {
      'no_listings': 'अभी कोई लिस्टिंग नहीं है।',
      'published': 'प्रकाशित',
      'closed': 'बंद',
      'draft': 'मसौदा',
      'cancelled': 'रद्द',
    },
    'mr': {
      'no_listings': 'अजून लिस्टिंग नाहीत.',
      'published': 'प्रकाशित',
      'closed': 'बंद',
      'draft': 'मसुदा',
      'cancelled': 'रद्द',
    },
    'ta': {
      'no_listings': 'இன்னும் பட்டியல்கள் இல்லை.',
      'published': 'வெளியிடப்பட்டது',
      'closed': 'மூடப்பட்டது',
      'draft': 'வரைவு',
      'cancelled': 'ரத்து செய்யப்பட்டது',
    },
    'ml': {
      'no_listings': 'ഇനിയും ലിസ്റ്റിംഗുകളില്ല.',
      'published': 'പ്രസിദ്ധീകരിച്ചു',
      'closed': 'അടച്ചു',
      'draft': 'കരട്',
      'cancelled': 'റദ്ദാക്കി',
    },
  };

  static String tr(String language, String key) {
    return values[language]?[key] ?? values['en']?[key] ?? key;
  }

  static String listingStatus(String language, String status) {
    switch (status) {
      case 'PUBLISHED':
        return tr(language, 'published');
      case 'CLOSED':
        return tr(language, 'closed');
      case 'DRAFT':
        return tr(language, 'draft');
      case 'CANCELLED':
        return tr(language, 'cancelled');
      default:
        return status;
    }
  }
}
