from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.service import append_event
from app.core.errors import AppError
from app.identity.profile_models import FarmerProfile
from app.livestock.models import EvidenceAsset, Goat, Lot, LotGoat
from app.livestock.schemas import EvidenceUploadRequest, GoatCreate, LotCreate


def farmer_profile_for_user(db: Session, user_id: UUID) -> FarmerProfile:
    profile = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user_id))
    if not profile:
        raise AppError("FARMER_PROFILE_REQUIRED", "Farmer profile is required.", 409)
    return profile


def create_goat(db: Session, user_id: UUID, payload: GoatCreate) -> Goat:
    farmer = farmer_profile_for_user(db, user_id)
    goat = Goat(
        goat_code=f"PS-G-{uuid4().hex[:8].upper()}",
        farmer_profile_id=farmer.id,
        breed=payload.breed,
        sex=payload.sex,
        age_months=payload.age_months,
        health_notes=payload.health_notes,
    )
    db.add(goat)
    db.flush()
    append_event(
        db,
        "GOAT",
        goat.id,
        "GOAT_REGISTERED",
        user_id,
        payload={"goat_code": goat.goat_code},
        commit=False,
    )
    db.commit()
    db.refresh(goat)
    return goat


def create_lot(db: Session, user_id: UUID, payload: LotCreate) -> tuple[Lot, list[Goat]]:
    farmer = farmer_profile_for_user(db, user_id)

    linked_goats: list[Goat] = []
    for goat_code in payload.goat_ids:
        goat = db.scalar(
            select(Goat).where(
                Goat.goat_code == goat_code,
                Goat.farmer_profile_id == farmer.id,
            )
        )
        if not goat:
            raise AppError(
                "GOAT_NOT_FOUND",
                f"Goat {goat_code} does not belong to this farmer.",
                404,
            )
        already_linked = db.scalar(select(LotGoat).where(LotGoat.goat_id == goat.id))
        if already_linked:
            raise AppError("GOAT_ALREADY_IN_LOT", f"Goat {goat_code} is already in a lot.", 409)
        linked_goats.append(goat)

    if payload.goat_ids and len(payload.goat_ids) > payload.declared_quantity:
        raise AppError(
            "LOT_QUANTITY_MISMATCH",
            "Linked goats cannot exceed declared lot quantity.",
            400,
        )

    lot = Lot(
        lot_code=f"PS-L-{uuid4().hex[:8].upper()}",
        farmer_profile_id=farmer.id,
        declared_quantity=payload.declared_quantity,
        breed_summary=payload.breed_summary,
        sex_summary=payload.sex_summary,
        age_summary=payload.age_summary,
        health_notes=payload.health_notes,
    )
    db.add(lot)
    db.flush()

    for goat in linked_goats:
        db.add(LotGoat(lot_id=lot.id, goat_id=goat.id))

    append_event(
        db,
        "LOT",
        lot.id,
        "LOT_REGISTERED",
        user_id,
        payload={
            "lot_code": lot.lot_code,
            "declared_quantity": lot.declared_quantity,
            "linked_goat_ids": [goat.goat_code for goat in linked_goats],
        },
        commit=False,
    )
    db.commit()
    db.refresh(lot)
    return lot, linked_goats


def create_evidence_upload_contract(
    db: Session,
    user_id: UUID,
    payload: EvidenceUploadRequest,
) -> tuple[EvidenceAsset, str]:
    farmer = farmer_profile_for_user(db, user_id)

    if payload.owner_type == "GOAT":
        owner = db.scalar(
            select(Goat).where(
                Goat.goat_code == payload.owner_id,
                Goat.farmer_profile_id == farmer.id,
            )
        )
    else:
        owner = db.scalar(
            select(Lot).where(
                Lot.lot_code == payload.owner_id,
                Lot.farmer_profile_id == farmer.id,
            )
        )
    if not owner:
        raise AppError("EVIDENCE_OWNER_NOT_FOUND", "Evidence owner not found.", 404)

    extension = payload.file_name.rsplit(".", 1)[-1].lower() if "." in payload.file_name else "bin"
    storage_key = f"livestock/{payload.owner_type.lower()}/{owner.id}/{uuid4().hex}.{extension}"

    asset = EvidenceAsset(
        owner_type=payload.owner_type,
        owner_id=owner.id,
        evidence_type=payload.evidence_type,
        storage_key=storage_key,
        mime_type=payload.mime_type,
        captured_by_user_id=user_id,
        status="PENDING_UPLOAD",
    )
    db.add(asset)
    db.flush()
    append_event(
        db,
        "EVIDENCE_ASSET",
        asset.id,
        "EVIDENCE_UPLOAD_CONTRACT_CREATED",
        user_id,
        payload={
            "owner_type": asset.owner_type,
            "owner_id": str(asset.owner_id),
            "evidence_type": asset.evidence_type,
            "storage_key": asset.storage_key,
        },
        commit=False,
    )
    db.commit()
    db.refresh(asset)

    # Placeholder development upload contract. Production uses object-storage presigned URLs.
    upload_url = f"http://localhost:8000/dev-upload/{asset.id}"
    return asset, upload_url
