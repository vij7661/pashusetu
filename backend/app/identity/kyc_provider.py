from dataclasses import dataclass

from app.core.config import get_settings
from app.core.errors import AppError
from app.db.qa_fixtures import QA_KYC_FIXTURES_BY_UID


@dataclass(frozen=True)
class KycVerificationResult:
    status: str
    masked_id: str
    provider_reference: str


class KycVerificationService:
    """Replaceable QA adapter. Raw identifiers are never returned or persisted."""

    def verify(self, aadhaar_number: str, name: str, consent: bool) -> KycVerificationResult:
        settings = get_settings()
        if not consent:
            raise AppError("KYC_CONSENT_REQUIRED", "Identity verification consent is required.", 422)
        if settings.app_env.lower() != "qa" or not settings.database_isolated_for_qa:
            raise AppError("KYC_PROVIDER_UNAVAILABLE", "KYC verification is unavailable.", 503)
        fixture = QA_KYC_FIXTURES_BY_UID.get(aadhaar_number)
        if fixture is None or fixture.name.casefold() != name.strip().casefold():
            raise AppError("QA_KYC_NOT_FOUND", "These QA KYC details could not be verified.", 422)
        return KycVerificationResult(
            status="QA_VERIFIED",
            masked_id=f"XXXXXXXX{aadhaar_number[-4:]}",
            provider_reference=f"QA-KYC-{fixture.fixture_id}",
        )
