import pytest
from pydantic import ValidationError

from app.identity.schemas import FarmerRegistrationStatus


def test_registration_status_matches_saved_details():
    before_details = FarmerRegistrationStatus(
        registration_id="REG-1",
        registration_status="NEW_IN_PROGRESS",
        next_step="FARMER_DETAILS",
        preferred_language="te",
    )
    after_details = FarmerRegistrationStatus(
        registration_id="REG-1",
        registration_status="NEW_IN_PROGRESS",
        next_step="KYC",
        full_name="Ramesh Goud",
        preferred_language="en",
    )

    assert before_details.next_step == "FARMER_DETAILS"
    assert after_details.next_step == "KYC"


def test_registration_status_rejects_inconsistent_or_unknown_state():
    with pytest.raises(ValidationError):
        FarmerRegistrationStatus(
            registration_id="REG-1",
            registration_status="NEW_IN_PROGRESS",
            next_step="HOME",
            preferred_language="te",
        )

    with pytest.raises(ValidationError):
        FarmerRegistrationStatus(
            registration_id="REG-1",
            registration_status="UNKNOWN",
            next_step="FARMER_DETAILS",
            preferred_language="te",
        )


def test_submitted_registration_can_only_resume_home():
    submitted = FarmerRegistrationStatus(
        registration_id="REG-1",
        registration_status="KYC_SUBMITTED",
        next_step="HOME",
        full_name="Ramesh Goud",
        preferred_language="te",
    )
    assert submitted.next_step == "HOME"

    with pytest.raises(ValidationError):
        FarmerRegistrationStatus(
            registration_id="REG-1",
            registration_status="KYC_SUBMITTED",
            next_step="KYC",
            full_name="Ramesh Goud",
            preferred_language="te",
        )
