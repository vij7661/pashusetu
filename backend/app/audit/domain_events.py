from uuid import UUID
from sqlalchemy.orm import Session

from app.audit.service import append_event


def transaction_event(db: Session, tx_id: UUID, event_type: str, actor_user_id=None, payload=None):
    return append_event(
        db,
        aggregate_type="TRANSACTION",
        aggregate_id=tx_id,
        event_type=event_type,
        actor_user_id=actor_user_id,
        payload=payload or {},
    )


def listing_event(db: Session, listing_id: UUID, event_type: str, actor_user_id=None, payload=None):
    return append_event(
        db,
        aggregate_type="LISTING",
        aggregate_id=listing_id,
        event_type=event_type,
        actor_user_id=actor_user_id,
        payload=payload or {},
    )


def weighment_event(db: Session, weighment_id: UUID, event_type: str, actor_user_id=None, payload=None):
    return append_event(
        db,
        aggregate_type="WEIGHMENT",
        aggregate_id=weighment_id,
        event_type=event_type,
        actor_user_id=actor_user_id,
        payload=payload or {},
    )
