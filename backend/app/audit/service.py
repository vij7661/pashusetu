from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit.models import AuditEvent


def append_event(
    db: Session,
    aggregate_type: str,
    aggregate_id: UUID,
    event_type: str,
    actor_user_id: UUID | None = None,
    request_id: str | None = None,
    payload: dict | None = None,
) -> AuditEvent:
    next_sequence = db.scalar(
        select(func.coalesce(func.max(AuditEvent.sequence), 0) + 1).where(
            AuditEvent.aggregate_type == aggregate_type,
            AuditEvent.aggregate_id == aggregate_id,
        )
    )
    event = AuditEvent(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        sequence=next_sequence,
        event_type=event_type,
        actor_user_id=actor_user_id,
        request_id=request_id,
        payload=payload or {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def events_for_aggregate(db: Session, aggregate_type: str, aggregate_id: UUID) -> list[AuditEvent]:
    return list(
        db.scalars(
            select(AuditEvent)
            .where(
                AuditEvent.aggregate_type == aggregate_type,
                AuditEvent.aggregate_id == aggregate_id,
            )
            .order_by(AuditEvent.sequence.asc())
        ).all()
    )
