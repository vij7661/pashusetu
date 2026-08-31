from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.reputation_models import OperatorScorecard, ReputationRecord
from app.transaction.models import Transaction
from app.weighment.models import WeighmentSession


def get_or_create_reputation(
    db: Session,
    subject_type: str,
    subject_id,
    *,
    commit: bool = True,
):
    row = db.scalar(
        select(ReputationRecord).where(
            ReputationRecord.subject_type == subject_type,
            ReputationRecord.subject_id == subject_id,
        )
    )
    if not row:
        row = ReputationRecord(subject_type=subject_type, subject_id=subject_id)
        db.add(row)
        if commit:
            db.commit()
            db.refresh(row)
        else:
            db.flush()
    return row


def close_transaction_reputation(
    db: Session,
    tx: Transaction,
    dispute_loser: str | None = None,
    *,
    commit: bool = True,
):
    farmer = get_or_create_reputation(
        db,
        "FARMER",
        tx.farmer_profile_id,
        commit=commit,
    )
    buyer = get_or_create_reputation(
        db,
        "BUYER",
        tx.buyer_profile_id,
        commit=commit,
    )

    farmer.completed_transactions += 1
    buyer.completed_transactions += 1

    if dispute_loser == "FARMER":
        farmer.disputes_lost += 1
        farmer.score = max(0, farmer.score - 5)
    elif dispute_loser == "BUYER":
        buyer.disputes_lost += 1
        buyer.score = max(0, buyer.score - 5)

    if commit:
        db.commit()
    else:
        db.flush()


def update_operator_scorecard_for_weighment(db: Session, weighment: WeighmentSession, is_reweigh: bool):
    row = db.scalar(
        select(OperatorScorecard).where(
            OperatorScorecard.operator_profile_id == weighment.operator_id
        )
    )
    if not row:
        row = OperatorScorecard(operator_profile_id=weighment.operator_id)
        db.add(row)
    row.weighment_count += 1
    if is_reweigh:
        row.reweigh_count += 1
    db.commit()
