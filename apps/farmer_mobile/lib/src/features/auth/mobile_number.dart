const int mobileNumberLength = 10;

bool isValidMobileNumber(String value) =>
    RegExp(r'^[0-9]{10}$').hasMatch(value);

String toIndiaE164(String value) => '+91$value';
