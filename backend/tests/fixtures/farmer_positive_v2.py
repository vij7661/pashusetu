"""Stable positive-path Farmer fixtures for registration-through-Home tests.

These are test identities, not production data. Raw Aadhaar is intentionally absent.
"""

from hashlib import sha256

OTP_SEED = "pashusetu-dev-otp-v1"
OTP_LENGTH = 4

_NAMES = [
    "Ramesh Goud", "Laxmi Narayana", "Mallesh Yadav", "Srinivas Reddy", "Anil Kumar",
    "Rajesh Naik", "Saidulu Goud", "Venkatesh", "Mahesh Reddy", "Narsimha",
    "Shankar Yadav", "Raju Goud", "Praveen Kumar", "Ravi Naik", "Suresh",
    "Kiran Reddy", "Ashok Yadav", "Madhava Rao", "Raghu", "Naveen",
    "Bhaskar", "Chandraiah", "Vijay Reddy", "Arun Kumar", "Gopal",
    "Harish Yadav", "Jagadeesh", "Krishna Goud", "Lingam", "Manoj",
    "Naresh", "Omkar", "Pavan Reddy", "Ravinder", "Satish",
    "Srikanth", "Teja", "Uday Kumar", "Vinod", "Yadagiri",
]

_LOCATIONS = [
    ("Nalgonda", "Chityal", "Chityal"),
    ("Warangal", "Hanamkonda", "Kazipet"),
    ("Suryapet", "Suryapet", "Pillalamarri"),
    ("Mahabubnagar", "Jadcherla", "Badepally"),
    ("Sangareddy", "Patancheru", "Isnapur"),
    ("Medak", "Toopran", "Ravelli"),
    ("Karimnagar", "Huzurabad", "Veenavanka"),
    ("Khammam", "Khammam Rural", "Kusumanchi"),
]

_LANGUAGES = ["te", "hi", "en", "mr", "ta", "ml"]


def development_otp(mobile_e164: str) -> str:
    digest = sha256(f"{OTP_SEED}:{mobile_e164}".encode()).hexdigest()
    value = int(digest[:8], 16) % (10**OTP_LENGTH)
    return f"{value:0{OTP_LENGTH}d}"


def _record(index: int) -> dict:
    mobile = f"+91910000{index:04d}"
    district, mandal, village = _LOCATIONS[(index - 1) % len(_LOCATIONS)]

    if index <= 16:
        state = "NEW_NOT_STARTED"
        farmer_id = None
        next_step = "FARMER_DETAILS"
        kyc_status = "NOT_SUBMITTED"
        details = False
    elif index <= 24:
        state = "NEW_IN_PROGRESS"
        farmer_id = None
        next_step = "KYC"
        kyc_status = "NOT_SUBMITTED"
        details = True
    elif index <= 32:
        state = "KYC_PENDING"
        farmer_id = f"F-FV2-{index:03d}"
        next_step = "HOME"
        kyc_status = "KYC_PENDING"
        details = True
    else:
        state = "KYC_VERIFIED"
        farmer_id = f"F-FV2-{index:03d}"
        next_step = "HOME"
        kyc_status = "KYC_VERIFIED"
        details = True

    return {
        "fixture_id": f"FV2-{index:03d}",
        "registration_id": f"REG-FV2-{index:03d}",
        "farmer_id": farmer_id,
        "mobile_e164": mobile,
        "dev_otp": development_otp(mobile),
        "full_name": _NAMES[index - 1] if details else None,
        "language": _LANGUAGES[(index - 1) % len(_LANGUAGES)],
        "village": village if details else None,
        "mandal": mandal if details else None,
        "district": district if details else None,
        "state": "Telangana" if details else None,
        "registration_state": state,
        "kyc_status": kyc_status,
        "expected_next_step": next_step,
    }


FARMER_POSITIVE_V2 = [_record(index) for index in range(1, 41)]
