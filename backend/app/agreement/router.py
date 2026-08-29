from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agreement.models import Agreement, AgreementConfirmation
from app.agreement.schemas import AgreementConfirmRequest, AgreementCreate, AgreementResponse
from app.agreement.service import confirm_agreement, create_agreement
from app.auth.dependencies import current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.identity.models import User
from app.transaction.models import Transaction
from app.transaction.service import transaction_for_party

router = APIRouter(prefix="/agreement", tags=["agreement"])


def _agreement_response(db: Session, tx: Transaction, agreement: Agreement) -> AgreementResponse:
    confirmations = db.scalars(
        select(AgreementConfirmation).where(AgreementConfirmation.agreement_id == agreement.id)
    ).all()
    farmer_confirmed = any(x.party_role == "FARMER" and x.confirmed for x in confirmations)
    buyer_confirmed = any(x.party_role == "BUYER" and x.confirmed for x in confirmations)
    return AgreementResponse(
        agreement_id=agreement.agreement_code,
        transaction_id=tx.transaction_code,
        version=agreement.version,
        price_basis=agreement.price_basis,
        pickup_point=agreement.pickup_point,
        final_weighing_point=agreement.final_weighing_point,
        tolerance_percent=agreement.tolerance_basis_points / 100,
        transport_responsibility=agreement.transport_responsibility,
        dispute_rule=agreement.dispute_rule,
        farmer_confirmed=farmer_confirmed,
        buyer_confirmed=buyer_confirmed,
        locked=agreement.locked,
        status=agreement.status,
        accepted_bid_id=str(agreement.accepted_bid_id),
        listing_id=str(agreement.listing_id),
        farmer_profile_id=str(agreement.farmer_profile_id),
        buyer_profile_id=str(agreement.buyer_profile_id),
        selected_goat_ids=[str(x) for x in (agreement.selected_goat_ids or [])],
        whole_lot=bool(agreement.whole_lot),
        accepted_price_per_kg_paise=agreement.accepted_price_per_kg_paise,
        agreed_weight_kg=float(agreement.agreed_weight_kg),
        livestock_amount_paise=agreement.livestock_amount_paise,
    )


@router.post("/transactions/{transaction_id}", response_model=AgreementResponse, status_code=201)
def post_agreement(
    transaction_id: str,
    payload: AgreementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    agreement = create_agreement(db, tx, user.id, payload)
    return _agreement_response(db, tx, agreement)


@router.post(
    "/transactions/{transaction_id}/{agreement_id}/confirm", response_model=AgreementResponse
)
def post_confirm(
    transaction_id: str,
    agreement_id: str,
    payload: AgreementConfirmRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    agreement = db.scalar(
        select(Agreement).where(
            Agreement.agreement_code == agreement_id,
            Agreement.transaction_id == tx.id,
        )
    )
    if not agreement:
        raise AppError("AGREEMENT_NOT_FOUND", "Agreement not found.", 404)
    agreement = confirm_agreement(db, tx, agreement, user.id, payload.confirm)
    return _agreement_response(db, tx, agreement)


@router.get("/transactions/{transaction_id}/active", response_model=AgreementResponse)
def get_active(
    transaction_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    tx = transaction_for_party(db, transaction_id, user.id)
    if not tx.active_agreement_id:
        raise AppError("ACTIVE_AGREEMENT_NOT_FOUND", "No active locked agreement.", 404)
    agreement = db.get(Agreement, tx.active_agreement_id)
    return _agreement_response(db, tx, agreement)
