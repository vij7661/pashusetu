from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.identity.profile_models import FarmerProfile
from app.livestock.models import Goat, Lot, LotGoat
from app.livestock.schemas import (
    GoatCreate,
    GoatResponse,
    LotCreate,
    LotResponse,
    EvidenceUploadRequest,
    EvidenceUploadResponse,
)
from app.livestock.service import (
    create_goat,
    create_lot,
    create_evidence_upload_contract,
    farmer_profile_for_user,
)

router = APIRouter(prefix="/livestock", tags=["livestock"])


@router.post("/goats", response_model=GoatResponse, status_code=201)
def post_goat(
    payload: GoatCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    g = create_goat(db, user.id, payload)
    return GoatResponse(
        goat_id=g.goat_code,
        breed=g.breed,
        sex=g.sex,
        age_months=g.age_months,
        health_notes=g.health_notes,
        status=g.status,
    )


@router.get("/goats/{goat_id}", response_model=GoatResponse)
def get_goat(
    goat_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    farmer = farmer_profile_for_user(db, user.id)
    g = db.scalar(
        select(Goat).where(Goat.goat_code == goat_id, Goat.farmer_profile_id == farmer.id)
    )
    if not g:
        raise AppError("GOAT_NOT_FOUND", "Goat not found.", 404)
    return GoatResponse(
        goat_id=g.goat_code,
        breed=g.breed,
        sex=g.sex,
        age_months=g.age_months,
        health_notes=g.health_notes,
        status=g.status,
    )


@router.post("/lots", response_model=LotResponse, status_code=201)
def post_lot(
    payload: LotCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    lot, linked = create_lot(db, user.id, payload)
    return LotResponse(
        lot_id=lot.lot_code,
        declared_quantity=lot.declared_quantity,
        linked_goat_ids=[g.goat_code for g in linked],
        breed_summary=lot.breed_summary,
        sex_summary=lot.sex_summary,
        age_summary=lot.age_summary,
        status=lot.status,
    )


@router.get("/lots/{lot_id}", response_model=LotResponse)
def get_lot(
    lot_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    farmer = farmer_profile_for_user(db, user.id)
    lot = db.scalar(
        select(Lot).where(Lot.lot_code == lot_id, Lot.farmer_profile_id == farmer.id)
    )
    if not lot:
        raise AppError("LOT_NOT_FOUND", "Lot not found.", 404)

    goat_ids = db.scalars(
        select(Goat.goat_code)
        .join(LotGoat, LotGoat.goat_id == Goat.id)
        .where(LotGoat.lot_id == lot.id)
    ).all()

    return LotResponse(
        lot_id=lot.lot_code,
        declared_quantity=lot.declared_quantity,
        linked_goat_ids=list(goat_ids),
        breed_summary=lot.breed_summary,
        sex_summary=lot.sex_summary,
        age_summary=lot.age_summary,
        status=lot.status,
    )


@router.post("/evidence/upload-contract", response_model=EvidenceUploadResponse, status_code=201)
def create_upload_contract(
    payload: EvidenceUploadRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    asset, url = create_evidence_upload_contract(db, user.id, payload)
    return EvidenceUploadResponse(
        evidence_id=str(asset.id),
        storage_key=asset.storage_key,
        upload_method="PUT",
        upload_url=url,
        expires_in_seconds=900,
    )
