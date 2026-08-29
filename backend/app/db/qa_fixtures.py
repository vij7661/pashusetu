from dataclasses import dataclass


@dataclass(frozen=True)
class QAUserFixture:
    fixture_id: str
    local_mobile: str
    role: str
    language: str

    @property
    def mobile_e164(self) -> str:
        return f"+91{self.local_mobile}"


QA_USERS = (
    QAUserFixture("FARMER_EN_001", "6123456789", "FARMER", "en"),
    QAUserFixture("FARMER_TE_001", "7234567890", "FARMER", "te"),
    QAUserFixture("FARMER_SUB3_001", "8345678901", "FARMER", "en"),
    QAUserFixture("BUYER_001", "9456789012", "BUYER", "en"),
    QAUserFixture("OPERATOR_001", "6789012345", "OPERATOR", "en"),
    QAUserFixture("ADMIN_001", "7890123456", "ADMIN", "en"),
)

QA_USERS_BY_ID = {fixture.fixture_id: fixture for fixture in QA_USERS}
QA_USERS_BY_MOBILE = {fixture.mobile_e164: fixture for fixture in QA_USERS}


@dataclass(frozen=True)
class QAKycFixture:
    fixture_id: str
    uid: str
    name: str


QA_KYC_FIXTURES = (
    QAKycFixture("KYC_FARMER_EN_001", "999941057058", "Shivshankar Choudhury"),
    QAKycFixture("KYC_FARMER_TE_001", "999971658847", "Kumar Agarwal"),
    QAKycFixture("KYC_FARMER_SUB3_001", "999933119405", "Fatima Bedi"),
)
QA_KYC_FIXTURES_BY_UID = {fixture.uid: fixture for fixture in QA_KYC_FIXTURES}

QA_CENTRE_CODE = "QA-CENTRE-001"
QA_SCALE_CODE = "QA-SCALE-001"
QA_VERIFIED_GOAT_CODES = ("QA-GOAT-EN-001", "QA-GOAT-EN-002", "QA-GOAT-EN-003")
QA_UNVERIFIED_GOAT_CODE = "QA-GOAT-TE-001"
QA_SUB3_GOAT_CODES = ("QA-GOAT-SUB3-001", "QA-GOAT-SUB3-002")
QA_VERIFIED_LOT_CODE = "QA-LOT-EN-003"
QA_SUB3_LOT_CODE = "QA-LOT-SUB3-002"
QA_LISTING_CODE = "QA-LISTING-LIVE-001"
QA_TEST_OTP = "4816"
