from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.db.session import get_db
from app.identity.models import User
from app.audit.service import events_for_aggregate

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/{aggregate_type}/{aggregate_id}")
def get_audit_events(
    aggregate_type: str,
    aggregate_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    events = events_for_aggregate(db, aggregate_type, UUID(aggregate_id))
    return [
        {
            "sequence": e.sequence,
            "event_type": e.event_type,
            "actor_user_id": str(e.actor_user_id) if e.actor_user_id else None,
            "request_id": e.request_id,
            "occurred_at": e.occurred_at,
            "payload": e.payload,
        }
        for e in events
    ]
