from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agreement.models import Agreement, AgreementConfirmation
from app.agreement.schemas import (
    PILOT_DISPUTE_RULE,
    PILOT_PRICE_BASIS,
    PILOT_TRANSPORT_RESPONSIBILITY,
    AgreementCreate,
)
from app.audit.service import append_event
from app.core.errors import AppError
from app.identity.profile_models import BuyerProfile, FarmerProfile
from app.marketplace.models import Bid
from app.transaction.models import Transaction
from app.transaction.service import transition_transaction


def _role_for_user(db: Session, tx: Transaction, user_id: UUID) -> str:
    farmer = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user_id))
    if farmer and farmer.id == tx.farmer_profile_id:
        return "FARMER"

    buyer = db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == user_id))
    if buyer and buyer.id == tx.buyer_profile_id:
        return "BUYER"

    raise AppError("FORBIDDEN", "User is not a transaction party.", 403)


def create_agreement(
    db: Session,
    tx: Transaction,
    user_id: UUID,
    payload: AgreementCreate,
) -> Agreement:
    role = _role_for_user(db, tx, user_id)
    if role != "FARMER":
        raise AppError("FARMER_ONLY", "Farmer creates the initial agreement proposal.", 403)
    if tx.state not in {"OFFER_ACCEPTED", "AGREEMENT_PENDING"}:
        raise AppError("AGREEMENT_NOT_ALLOWED", "Agreement cannot be created in current state.", 409)

    accepted_bid = db.get(Bid, tx.accepted_bid_id)
    if not accepted_bid:
        raise AppError("ACCEPTED_BID_NOT_FOUND", "Accepted bid not found.", 500)

    next_version = db.scalar(
        select(func.coalesce(func.max(Agreement.version), 0) + 1).where(
            Agreement.transaction_id == tx.id
        )
    )

    agreement = Agreement(
        agreement_code=f"AGR-{uuid4().hex[:10].upper()}",
        transaction_id=tx.id,
        version=next_version,
        accepted_bid_id=accepted_bid.id,
        price_basis=PILOT_PRICE_BASIS,
        pickup_point=payload.pickup_point,
        final_weighing_point=payload.final_weighing_point,
        tolerance_basis_points=int(Decimal(str(payload.tolerance_percent)) * Decimal(100)),
        transport_responsibility=PILOT_TRANSPORT_RESPONSIBILITY,
        dispute_rule=PILOT_DISPUTE_RULE,
        status="PENDING_CONFIRMATION",
        locked=False,
    )
    db.add(agreement)
    db.flush()

    if tx.state == "OFFER_ACCEPTED":
        transition_transaction(db, tx, "AGREEMENT_PENDING", commit=False)

    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "AGREEMENT_CREATED",
        user_id,
        payload={
            "agreement_id": agreement.agreement_code,
            "version": agreement.version,
        },
        commit=False,
    )
    db.commit()
    db.refresh(agreement)
    return agreement


def confirm_agreement(
    db: Session,
    tx: Transaction,
    agreement: Agreement,
    user_id: UUID,
    confirm: bool,
) -> Agreement:
    if agreement.locked:
        return agreement
    if tx.state != "AGREEMENT_PENDING":
        raise AppError("AGREEMENT_NOT_PENDING", "Transaction is not awaiting agreement confirmation.", 409)

    role = _role_for_user(db, tx, user_id)
    existing = db.scalar(
        select(AgreementConfirmation).where(
            AgreementConfirmation.agreement_id == agreement.id,
            AgreementConfirmation.party_role == role,
        )
    )
    if existing:
        existing.confirmed = confirm
        existing.user_id = user_id
    else:
        db.add(
            AgreementConfirmation(
                agreement_id=agreement.id,
                party_role=role,
                user_id=user_id,
                confirmed=confirm,
            )
        )
    db.flush()

    append_event(
        db,
        "TRANSACTION",
        tx.id,
        "AGREEMENT_CONFIRMATION_RECORDED",
        user_id,
        payload={
            "agreement_id": agreement.agreement_code,
            "party_role": role,
            "confirmed": confirm,
        },
        commit=False,
    )

    confirmations = db.scalars(
        select(AgreementConfirmation).where(
            AgreementConfirmation.agreement_id == agreement.id,
            AgreementConfirmation.confirmed.is_(True),
        )
    ).all()
    confirmed_roles = {x.party_role for x in confirmations}

    if {"FARMER", "BUYER"} <= confirmed_roles:
        agreement.locked = True
        agreement.status = "LOCKED"
        tx.active_agreement_id = agreement.id
        transition_transaction(db, tx, "AGREEMENT_LOCKED", commit=False)
        append_event(
            db,
            "TRANSACTION",
            tx.id,
            "AGREEMENT_LOCKED",
            user_id,
            payload={
                "agreement_id": agreement.agreement_code,
                "version": agreement.version,
            },
            commit=False,
        )

    db.commit()
    db.refresh(agreement)
    return agreement
