"""Seed explicit Farmer lifecycle checkpoints for local/development QA only."""

from sqlalchemy import select

from app.auth.service import DEVELOPMENT_ENVS
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.identity.models import User
from app.identity.profile_models import FarmerRegistration

REGISTRATION_STARTED_MOBILE = "+919100000009"


def seed_lifecycle_qa() -> None:
    settings = get_settings()
    if settings.app_env.lower() not in DEVELOPMENT_ENVS:
        raise RuntimeError(
            "Farmer lifecycle QA fixtures are forbidden outside local/test/development."
        )

    db = SessionLocal()
    try:
        existing_user = db.scalar(
            select(User).where(User.mobile_e164 == REGISTRATION_STARTED_MOBILE)
        )
        if existing_user is not None:
            raise RuntimeError(
                f"{REGISTRATION_STARTED_MOBILE} must not have a Farmer account for the "
                "REGISTRATION_STARTED fixture. Reset/reseed the QA database."
            )

        registration = db.scalar(
            select(FarmerRegistration).where(
                FarmerRegistration.mobile_e164 == REGISTRATION_STARTED_MOBILE
            )
        )
        if registration is None:
            registration = FarmerRegistration(
                registration_code="REG-FLC-009",
                mobile_e164=REGISTRATION_STARTED_MOBILE,
                status="NEW_IN_PROGRESS",
                preferred_language="en",
            )
            db.add(registration)
        else:
            if registration.user_id is not None:
                raise RuntimeError(
                    "REGISTRATION_STARTED fixture is already linked to an account; "
                    "reset/reseed the QA database."
                )
            registration.status = "NEW_IN_PROGRESS"
            registration.preferred_language = "en"
            registration.full_name = None
            registration.village = None
            registration.mandal = None
            registration.district = None
            registration.state = None
            registration.kyc_reference = None

        db.commit()
        print("Farmer lifecycle QA checkpoint ready")
        print("FLC-009 REGISTRATION_STARTED -> +919100000009")
    finally:
        db.close()


if __name__ == "__main__":
    seed_lifecycle_qa()
