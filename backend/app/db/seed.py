from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.identity.models import User, UserRole
from app.identity.profile_models import BuyerProfile, FarmerProfile
from app.weighment.models import MandalCentre, OperatorProfile, ScaleDevice


def run_seed():
    db = SessionLocal()
    try:
        if db.scalar(select(MandalCentre).limit(1)):
            print("Seed data already present.")
            return

        centre = MandalCentre(
            centre_code="CHY-02",
            name="Chityal Mandal Centre",
            village="Chityal",
            mandal="Chityal",
            district="Nalgonda",
            state="Telangana",
            latitude=Decimal("17.232100"),
            longitude=Decimal("79.137400"),
        )
        db.add(centre)
        db.flush()

        farmer_user = User(mobile_e164="+919876543210", preferred_language="te")
        buyer_user = User(mobile_e164="+919876512345", preferred_language="te")
        operator_user = User(mobile_e164="+919876500017", preferred_language="te")
        db.add_all([farmer_user, buyer_user, operator_user])
        db.flush()

        db.add_all(
            [
                UserRole(user_id=farmer_user.id, role="FARMER"),
                UserRole(user_id=buyer_user.id, role="BUYER"),
                UserRole(user_id=operator_user.id, role="OPERATOR"),
            ]
        )

        db.add(
            FarmerProfile(
                user_id=farmer_user.id,
                farmer_code="PS-F-DEMO01",
                full_name="Ramesh",
                village="Chityal",
                mandal="Chityal",
                district="Nalgonda",
                state="Telangana",
                kyc_status="VERIFIED",
                payout_status="VERIFIED",
            )
        )
        db.add(
            BuyerProfile(
                user_id=buyer_user.id,
                buyer_code="PS-B-DEMO01",
                business_name="Hyderabad Meat Traders",
                contact_person="Imran",
                buyer_type="BULK_BUYER",
                city="Hyderabad",
                state="Telangana",
                kyc_status="VERIFIED",
                business_verified=True,
            )
        )
        db.add(
            OperatorProfile(
                user_id=operator_user.id,
                operator_code="OP-DEMO01",
                full_name="Suresh",
                centre_id=centre.id,
            )
        )
        db.add(
            ScaleDevice(
                scale_code="A-114",
                centre_id=centre.id,
                vendor="SIMULATED",
                model="DEV-SCALE",
                bluetooth_identifier="SIM-A114",
                calibration_status="VALID",
            )
        )
        db.commit()
        print("PashuSetu demo seed created.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
